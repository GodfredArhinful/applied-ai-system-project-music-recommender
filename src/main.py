from src.recommender import load_songs, recommend_songs

def print_ascii_table(recommendations, title):
    # Challenge 4: Visual Summary Table Output
    print("\n" + "="*112)
    print(f" {title.upper()} ")
    print("="*112)
    print(f"{'#':<3} | {'Song':<35} | {'Score':<6} | {'Reasons'}")
    print("-" * 112)
    for i, rec in enumerate(recommendations, 1):
        song, score, explanation = rec
        name_str = f"{song['title']} by {song['artist']}"
        # Format explicitly for clean table UI
        print(f"{i:<3} | {name_str[:35]:<35} | {score:<6.2f} | {explanation}")
    print("-" * 112)

def main() -> None:
    songs = load_songs("data/songs.csv") 

    # We will test two modes from Challenge 2 with the advanced properties!
    user_profiles = {
        "Old-School Rocker (Genre-First Mode)": {
            "mode": "genre_first",
            "prefs": {"genre": "rock", "mood": "intense", "target_decade": 2000, "target_tag": "aggressive"}
        },
        "Trendy Workout (Energy-Focused Mode)": {
            "mode": "energy_focused",
            "prefs": {"energy": 0.95, "min_popularity": 80, "target_tag": "euphoric"}
        }
    }

    for profile_name, config in user_profiles.items():
        mode = config["mode"]
        prefs = config["prefs"]
        
        # Pull top 4 to hopefully visibly trigger the Diversity Penalty for repeated musicians
        recommendations = recommend_songs(prefs, songs, k=4, mode=mode)
        
        print_ascii_table(recommendations, f"TOP RECS FOR: {profile_name}")

if __name__ == "__main__":
    main()
