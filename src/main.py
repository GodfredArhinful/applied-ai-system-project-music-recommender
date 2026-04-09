"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv") 

    # Step 1: Stress Test with Diverse Profiles + Edge Case
    user_profiles = {
        "High-Energy Pop (Vibe: Pop, Happy, 0.9)": {"genre": "pop", "mood": "happy", "energy": 0.9},
        "Chill Lofi (Vibe: Lofi, Chill, 0.3)": {"genre": "lofi", "mood": "chill", "energy": 0.3},
        "Deep Intense Rock (Vibe: Rock, Intense, 0.85)": {"genre": "rock", "mood": "intense", "energy": 0.85},
        # Edge case: Conflicting preferences (EDM is typically energetic/happy, user wants sad but high energy)
        "Edge Case Sad EDM (Vibe: EDM, Sad, 0.95)": {"genre": "edm", "mood": "sad", "energy": 0.95}
    }

    for profile_name, user_prefs in user_profiles.items():
        recommendations = recommend_songs(user_prefs, songs, k=3)

        print("\n" + "="*60)
        print(f" 🎧 TOP RECOMMENDATIONS FOR: {profile_name} 🎧")
        print("="*60 + "\n")
        for i, rec in enumerate(recommendations, 1):
            song, score, explanation = rec
            print(f"#{i} | {song['title']} by {song['artist']}")
            print(f"    🌟 Score: {score:.2f} / 4.00")
            print(f"    💡 Why?   {explanation}")
            print("-" * 60)


if __name__ == "__main__":
    main()
