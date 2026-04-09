from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import csv

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        scored_songs = [(song, self._score_song(user, song)) for song in self.songs]
        # Using the sorted() method as discussed!
        ranked_list = sorted(scored_songs, key=lambda x: x[1], reverse=True)
        return [item[0] for item in ranked_list[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        reasons = []
        if song.genre.lower() == user.favorite_genre.lower():
            reasons.append("Genre match (+2.0)")
        if song.mood.lower() == user.favorite_mood.lower():
            reasons.append("Mood match (+1.0)")
        energy_score = max(0.0, 1.0 - abs(song.energy - user.target_energy))
        reasons.append(f"Energy match (+{energy_score:.2f})")
        return ", ".join(reasons)

    def _score_song(self, user: UserProfile, song: Song) -> float:
        """Returns a numeric score representing user preference compatibility."""
        score = 0.0
        if song.genre.lower() == user.favorite_genre.lower():
            score += 1.0
        if song.mood.lower() == user.favorite_mood.lower():
            score += 1.0
        score += max(0.0, 1.0 - abs(song.energy - user.target_energy)) * 2.0
        return score

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    songs = []
    try:
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert numerical fields to appropriate types
                row['id'] = int(row['id'])
                row['energy'] = float(row['energy'])
                row['tempo_bpm'] = float(row['tempo_bpm'])
                row['valence'] = float(row['valence'])
                row['danceability'] = float(row['danceability'])
                row['acousticness'] = float(row['acousticness'])
                songs.append(row)
    except FileNotFoundError:
        print(f"Error: Could not find {csv_path}")
    
    print(f"Loaded songs: {len(songs)}")
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py
    """
    score = 0.0
    reasons = []

    # 1. Genre Match (+1.0 point) [WEIGHT SHIFT EXPERIMENT: Halved from 2.0]
    if song.get("genre", "").lower() == user_prefs.get("genre", "").lower():
        score += 1.0
        reasons.append("Genre match (+1.0)")

    # 2. Mood Match (+1.0 point)
    if song.get("mood", "").lower() == user_prefs.get("mood", "").lower():
        score += 1.0
        reasons.append("Mood match (+1.0)")

    # 3. Energy Similarity (Up to +2.0 points) [WEIGHT SHIFT EXPERIMENT: Doubled from 1.0]
    if "energy" in user_prefs and "energy" in song:
        energy_diff = abs(song["energy"] - user_prefs["energy"])
        energy_score = max(0.0, 1.0 - energy_diff) * 2.0
        score += energy_score
        reasons.append(f"Energy match (+{energy_score:.2f})")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    scored_songs = []
    
    # Loop through all songs and score them
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        
        # Combine the reasons into a single string explanation
        explanation = ", ".join(reasons) if reasons else "No specific matches"
        
        # Add a tuple of (song_dict, score, explanation) to our list
        scored_songs.append((song, score, explanation))
        
    # Pythonic sorting: we use the sorted() method to return a completely new sorted list.
    # The lambda tells the sort function to look at the second item (index 1) which is the score.
    # reverse=True ensures we get the highest scores first.
    ranked_list = sorted(scored_songs, key=lambda x: x[1], reverse=True)
    
    # Return only the top k results (using list slicing)
    return ranked_list[:k]
