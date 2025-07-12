import pandas as pd

def get_maps(team1="Team A", team2="Team B"):
    df = pd.read_csv("map_preferences.csv")

    # Rename columns to be generic if needed
    df["PickWeight"] = df.get(f"PickWeight_{team1}", 0)
    df["BanWeight"] = df.get(f"BanWeight_{team1}", 0)
    df["Preference"] = df.get(f"TotalPreference_{team1}", 0)
    
    return df[["Map", "PickWeight", "BanWeight", "Preference"]]
    return pd.read_csv("maps.csv")
