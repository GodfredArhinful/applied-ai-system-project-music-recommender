import os
import logging
import csv
from typing import List, Dict, Tuple, Optional
from dotenv import load_dotenv

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError:
    logging.warning("Please install sentence-transformers and scikit-learn to use the AI DJ.")
    SentenceTransformer = None

try:
    import google.generativeai as genai
except ImportError:
    logging.warning("Please install google-generativeai to use the AI DJ generation.")
    genai = None

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class AIDJ:
    def __init__(self, songs: List[Dict]):
        self.songs = songs
        self.model = None
        self.song_embeddings = None
        self.generation_ready = False
        self.artist_bios = self._load_artist_bios("data/artist_bios.csv")
        
        # Load environment variables (API Key)
        load_dotenv()
        self._setup_generation_api()

    def _load_artist_bios(self, filepath: str) -> Dict[str, str]:
        bios = {}
        try:
            with open(filepath, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    bios[row['artist']] = row['bio']
        except FileNotFoundError:
            logging.warning(f"Artist bios file not found at {filepath}. RAG enhancement will be skipped.")
        return bios
        
    def _setup_generation_api(self):
        """Sets up the Gemini API for generation if the key is available."""
        api_key = os.getenv("GEMINI_API_KEY")
        if genai and api_key and api_key != "your_api_key_here":
            try:
                genai.configure(api_key=api_key)
                self.llm = genai.GenerativeModel('gemini-1.5-flash')
                self.generation_ready = True
                logging.info("Gemini API successfully configured.")
            except Exception as e:
                logging.error(f"Failed to configure Gemini API: {e}")
        else:
            logging.warning("GEMINI_API_KEY not found in environment or is invalid. Generation step will be skipped.")

    def _initialize_retriever(self):
        """Lazy load the sentence transformer to save startup time if not used."""
        if SentenceTransformer is None:
            raise RuntimeError("SentenceTransformer library not found.")
            
        if self.model is None:
            logging.info("Loading embedding model (this may take a moment on first run)...")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            
        if self.song_embeddings is None:
            logging.info("Embedding song catalog and artist bios for retrieval...")
            song_texts = []
            for s in self.songs:
                # STRETCH GOAL 1: RAG ENHANCEMENT (Multiple Data Sources)
                # We combine the song metadata WITH the artist bio into the semantic index
                artist_name = s.get('artist')
                bio = self.artist_bios.get(artist_name, "No bio available.")
                
                text = f"Title: {s.get('title')} by {artist_name}. " \
                       f"Genre: {s.get('genre')}. Mood: {s.get('mood')}. " \
                       f"Energy: {s.get('energy')}. " \
                       f"Tags: {s.get('detailed_mood_tags', '')}. " \
                       f"Artist Bio: {bio}"
                song_texts.append(text)
            self.song_embeddings = self.model.encode(song_texts)
            logging.info("Catalog embedding complete.")

    def retrieve(self, query: str, k: int = 3) -> List[Tuple[Dict, float]]:
        """Retrieves the top k most semantically similar songs to the query."""
        self._initialize_retriever()
        
        logging.info(f"Retrieving matches for query: '{query}'")
        query_embedding = self.model.encode([query])
        
        # Calculate cosine similarity between query and all songs
        similarities = cosine_similarity(query_embedding, self.song_embeddings)[0]
        
        # Get top K indices
        top_indices = similarities.argsort()[-k:][::-1]
        
        results = []
        for idx in top_indices:
            results.append((self.songs[idx], float(similarities[idx])))
            
        return results

    def _agent_decision(self, retrieved_items: List[Tuple[Dict, float]]) -> Optional[str]:
        """
        STRETCH GOAL 3: AGENTIC WORKFLOW ENHANCEMENT
        The Agent evaluates the retrieval scores before blindly passing them to the LLM.
        If the highest score is below a strict threshold, the agent decides it's a bad match
        and triggers a fallback response instead of hallucinating.
        """
        if not retrieved_items:
            return "Agent Error: No songs retrieved."
            
        top_score = retrieved_items[0][1]
        threshold = 0.15 # Minimum similarity threshold
        
        if top_score < threshold:
            logging.info(f"Agentic Check: Top score {top_score:.2f} is below threshold {threshold}. Triggering fallback.")
            return f"Whoa there, caller! I searched the crates but I ain't got nothing that matches that exact vibe right now. The closest thing I got only scored a {top_score:.2f} match. Try asking for some chill lo-fi, heavy rock, or 90s ambient!"
            
        logging.info(f"Agentic Check Passed: Top score {top_score:.2f} >= {threshold}.")
        return None

    def generate(self, query: str, retrieved_songs: List[Tuple[Dict, float]]) -> str:
        """Generates a personalized response using the LLM based on retrieved songs."""
        
        # STRETCH GOAL 3: Execute Agentic Workflow Step
        agent_fallback = self._agent_decision(retrieved_songs)
        if agent_fallback:
            return agent_fallback # Bypass LLM if agent deems it a bad match
            
        if not self.generation_ready:
            return "[Generation Skipped: Valid GEMINI_API_KEY not found. Please set it in your .env file.]\n" + \
                   "Here are the retrieved songs based on semantic search:\n" + \
                   "\n".join([f"- {s['title']} by {s['artist']} (Match: {score:.2f})" for s, score in retrieved_songs])

        logging.info("Generating personalized AI DJ response...")
        
        # Construct the context prompt, including the RAG enhanced Artist Bios
        context_parts = []
        for idx, (song, score) in enumerate(retrieved_songs, 1):
            bio = self.artist_bios.get(song['artist'], "")
            context_parts.append(f"Track {idx}: {song['title']} by {song['artist']}. Genre: {song['genre']}. Bio: {bio}")
        context_str = "\n".join(context_parts)
        
        # STRETCH GOAL 2: FINE-TUNING / SPECIALIZATION (Few-Shot Pattern)
        prompt = f"""
You are "DJ VibeZ", an intense, nostalgic 1990s underground pirate radio host. You speak entirely in 90s slang (like "rad", "fly", "dope", "da bomb", "word"). You always refer to your audience as "listeners on the dial" and you frequently make text-based DJ sound effects (like *wicka-wicka-scratch* or *AIR HORN*).

Here are two examples of how you MUST speak:

[EXAMPLE 1]
User: Give me something chill for coding.
Context: Midnight Coding by LoRoom. Bio: An anonymous lo-fi producer who streams chill beats 24/7.
DJ VibeZ: *wicka-wicka-scratch* Yoooo you are locked in with DJ VibeZ on the underground frequency! To the coder out there looking for chill vibes, this next track is da bomb. I'm spinning "Midnight Coding" by LoRoom. Word on the street is this cat streams chill beats 24/7! Keep it fly and stay locked to the dial! *AIR HORN*

[EXAMPLE 2]
User: Play a heavy workout song.
Context: Thunder Forge by Iron Skies. Bio: A heavy metal band from the 2000s.
DJ VibeZ: *AIR HORN* *AIR HORN* It's gettin' crazy up in the studio! Listeners on the dial, if you're hitting the iron, you need this phat track. Dropping "Thunder Forge" by the legendary Iron Skies! They've been crushing the underground since the 2000s and this track is strictly dope! *wicka-wicka*

Now, respond to this new caller!
User: "{query}"

Retrieved Database Tracks to spin:
{context_str}

DJ VibeZ:
"""
        try:
            response = self.llm.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logging.error(f"Error during LLM generation: {e}")
            return "Sorry, I encountered an error while trying to generate a response."

    def process_request(self, query: str, k: int = 3) -> Tuple[List[Dict], str]:
        """Full RAG Pipeline: Retrieves songs and generates a response."""
        retrieved_items = self.retrieve(query, k=k)
        response_text = self.generate(query, retrieved_items)
        
        # Just return the song dictionaries for the frontend if needed
        songs_only = [item[0] for item in retrieved_items]
        return songs_only, response_text

