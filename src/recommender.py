from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import csv

@dataclass
class Song:
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
    popularity: int = 50
    release_decade: int = 2000
    detailed_mood_tags: str = ""

@dataclass
class UserProfile:
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    target_decade: int = 2000

class Recommender:
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        scored_songs = [(song, self._score_song(user, song)) for song in self.songs]
        ranked_list = sorted(scored_songs, key=lambda x: x[1], reverse=True)
        return [item[0] for item in ranked_list[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        return "Explanation placeholder"

    def _score_song(self, user: UserProfile, song: Song) -> float:
        score = 0.0
        if song.genre.lower() == user.favorite_genre.lower():
            score += 1.0
        if song.mood.lower() == user.favorite_mood.lower():
            score += 1.0
        score += max(0.0, 1.0 - abs(song.energy - user.target_energy)) * 2.0
        return score

def load_songs(csv_path: str) -> List[Dict]:
    songs = []
    try:
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                row['id'] = int(row['id'])
                row['energy'] = float(row['energy'])
                row['tempo_bpm'] = float(row['tempo_bpm'])
                row['valence'] = float(row['valence'])
                row['danceability'] = float(row['danceability'])
                row['acousticness'] = float(row['acousticness'])
                
                # Challenge 1: New Features
                row['popularity'] = int(row.get('popularity', 50))
                row['release_decade'] = int(row.get('release_decade', 2000))
                songs.append(row)
    except FileNotFoundError:
        print(f"Error: Could not find {csv_path}")
    
    return songs


# ====== Challenge 2: Strategy Pattern for multiple scoring modes ======
def score_genre_first(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    score = 0.0
    reasons = []
    if song.get("genre", "").lower() == user_prefs.get("genre", "").lower():
        score += 3.0
        reasons.append("Huge Genre match (+3.0)")
    
    if song.get("mood", "").lower() == user_prefs.get("mood", "").lower():
        score += 0.5
        reasons.append("Mood match (+0.5)")
        
    return _apply_advanced_features(score, reasons, user_prefs, song)

def score_energy_focused(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    score = 0.0
    reasons = []
    energy_diff = abs(song.get("energy", 0.5) - user_prefs.get("energy", 0.5))
    energy_score = max(0.0, 1.0 - energy_diff) * 4.0
    score += energy_score
    reasons.append(f"Huge Energy match (+{energy_score:.2f})")
    
    if song.get("genre", "").lower() == user_prefs.get("genre", "").lower():
        score += 0.5
        reasons.append("Genre match (+0.5)")
        
    return _apply_advanced_features(score, reasons, user_prefs, song)

def _apply_advanced_features(base_score: float, reasons: List[str], user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    # 1. Popularity Boost (Challenge 1)
    if "min_popularity" in user_prefs and song.get("popularity", 0) >= user_prefs["min_popularity"]:
        base_score += 0.5
        reasons.append("Popularity requirement met (+0.5)")
        
    # 2. Release Decade Match (Challenge 1)
    if "target_decade" in user_prefs and song.get("release_decade") == user_prefs["target_decade"]:
        base_score += 1.0
        reasons.append(f"Decade {user_prefs['target_decade']} match (+1.0)")
        
    # 3. Detailed Mood Tag Check (Challenge 1)
    target_tag = user_prefs.get("target_tag")
    if target_tag and target_tag in song.get("detailed_mood_tags", ""):
        base_score += 1.5
        reasons.append(f"Detailed Tag '{target_tag}' match (+1.5)")
        
    return base_score, reasons

# Dictionary holding our strategies
SCORING_MODES = {
    "genre_first": score_genre_first,
    "energy_focused": score_energy_focused
}

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5, mode: str = "genre_first") -> List[Tuple[Dict, float, str]]:
    scored_songs = []
    scoring_func = SCORING_MODES.get(mode, score_genre_first)
    
    for song in songs:
        score, reasons = scoring_func(user_prefs, song)
        explanation = ", ".join(reasons) if reasons else "No specific matches"
        scored_songs.append((song, score, explanation))
        
    ranked_list = sorted(scored_songs, key=lambda x: x[1], reverse=True)
    
    # ====== Challenge 3: Diversity Penalty ======
    final_recs = []
    seen_artists = set()
    for song, score, exp in ranked_list:
        if song["artist"] in seen_artists:
            score -= 1.5
            exp += " [Penalty: Repeated Artist (-1.5)]"
        
        final_recs.append((song, score, exp))
        seen_artists.add(song["artist"])
        
    # Sort again after applying penalties
    final_recs = sorted(final_recs, key=lambda x: x[1], reverse=True)
    return final_recs[:k]

# For backwards compatibility with tests
def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    return score_genre_first(user_prefs, song)
