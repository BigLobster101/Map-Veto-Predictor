import streamlit as st
import pandas as pd
import numpy as np

# Map pool you gave me
MAP_POOL = [
    "Bank", "Border", "Chalet", "Clubhouse", "Consulate",
    "Kafe Dostoyevsky", "Lair", "Nighthaven Labs", "Skyscraper"
]

st.title("Rainbow Six Siege Map Veto Predictor")

st.markdown("""
Paste your veto data below, or edit it directly like an Excel sheet.  
Columns should be: Team 1, Team 2, Ban Style, Veto 1 ... Veto 9
""")

# Expected columns
default_cols = [
    "Team 1", "Team 2", "Ban Style",
    "Veto 1", "Veto 2", "Veto 3", "Veto 4", "Veto 5",
    "Veto 6", "Veto 7", "Veto 8", "Veto 9"
]

# Empty dataframe with columns
df = pd.DataFrame(columns=default_cols)

# Data editor for paste/edit
edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

if not edited_df.empty:
    # Clean data
    edited_df.columns = edited_df.columns.str.strip()
    for col in edited_df.columns:
        if edited_df[col].dtype == object:
            edited_df[col] = edited_df[col].astype(str).str.strip()
    edited_df["Ban Style"] = edited_df["Ban Style"].str.upper()
    for i in range(1, 10):
        col = f"Veto {i}"
        if col in edited_df.columns:
            edited_df[col] = edited_df[col].str.title()

    # Validate maps
    all_maps = set(pd.unique(edited_df[[f"Veto {i}" for i in range(1,10)]].values.ravel()))
    all_maps.discard('')  # remove empty string
    invalid_maps = all_maps - set(MAP_POOL)
    if invalid_maps:
        st.warning(f"Unknown maps detected in veto columns: {invalid_maps}")

    # Show cleaned preview
    st.subheader("Cleaned Data Preview")
    st.dataframe(edited_df)

    # Select teams to simulate
    team1_sim = st.selectbox("Select Team 1 for Simulation", options=sorted(edited_df["Team 1"].unique()))
    team2_sim = st.selectbox("Select Team 2 for Simulation", options=sorted(edited_df["Team 2"].unique()))

    # Filter data for those teams
    filtered_df = edited_df[(edited_df["Team 1"] == team1_sim) & (edited_df["Team 2"] == team2_sim)]

    st.write(f"Filtered {len(filtered_df)} veto phases between {team1_sim} and {team2_sim}")

    # ---------------------------------------------------------
    # Weighted preference calculation function
    # ---------------------------------------------------------
    def calculate_team_map_preferences(data):
        # Define weights by veto step for BO1 and BO3 (example weights)
        weights_bo1 = [-5, -4, -3, -2, -1, 1, 2, 3, 4]  # early ban strongly disliked, late ban less disliked, late picks liked
        weights_bo3 = [-5, -4, -3, -2, -1, 1, 2, 3, 4]  # can customize per step

        team_scores = {}
        for _, row in data.iterrows():
            ban_style = row["Ban Style"]
            weights = weights_bo1 if ban_style == "BO1" else weights_bo3
            for i in range(1, 10):
                map_name = row[f"Veto {i}"]
                if map_name == '' or map_name not in MAP_POOL:
                    continue
                # Assign scores to Team 1
                if row["Team 1"] not in team_scores:
                    team_scores[row["Team 1"]] = {m: 0 for m in MAP_POOL}
                # Assign scores to Team 2
                if row["Team 2"] not in team_scores:
                    team_scores[row["Team 2"]] = {m: 0 for m in MAP_POOL}

                # Team 1 score add
                team_scores[row["Team 1"]][map_name] += weights[i-1]
                # Team 2 score add (invert order of veto for team 2)
                team_scores[row["Team 2"]][map_name] += weights[8 - (i-1)]
        return team_scores

    # ---------------------------------------------------------
    # Veto simulation based on preferences
    # ---------------------------------------------------------
    def simulate_veto(team1, team2, team_prefs, ban_style):
        # Ban order depends on ban_style, simple example:
        if ban_style == "BO1":
            banning_order = [team1, team2] * 3 + [team1]
            picks_needed = 1
        else:
            banning_order = [team1, team2] * 2 + [team1, team2] + [team1, team2]  # example for BO3
            picks_needed = 3

        available_maps = set(MAP_POOL)
        bans = []
        picks = []

        for i, team in enumerate(banning_order):
            # Skip if picks filled
            if len(picks) >= picks_needed:
                break
            prefs = team_prefs.get(team, {m: 0 for m in MAP_POOL})

            # Team picks or bans the map with worst score for bans or best for picks
            # We treat odd veto numbers as bans, even as picks here for simplicity
            is_ban = (i < len(banning_order) - picks_needed)

            # Filter available maps and scores
            maps_scores = {m: prefs[m] for m in available_maps}

            if is_ban:
                # Ban the map team dislikes most (lowest score)
                map_to_ban = min(maps_scores, key=maps_scores.get)
                bans.append((team, map_to_ban))
                available_maps.remove(map_to_ban)
            else:
                # Pick the map team likes most (highest score)
                map_to_pick = max(maps_scores, key=maps_scores.get)
                picks.append((team, map_to_pick))
                available_maps.remove(map_to_pick)

        return bans, picks

    # ---------------------------------------------------------
    # Calculate preferences
    # ---------------------------------------------------------
    team_preferences = calculate_team_map_preferences(edited_df)

    # ---------------------------------------------------------
    # Tabs for Map Preference and Simulation
    # ---------------------------------------------------------
    tab1, tab2 = st.tabs(["Team Map Preferences", "Veto Simulation"])

    with tab1:
        st.subheader("Team Map Preference Scores")
        # Show scores in a dataframe format: team rows, map columns
        df_scores = pd.DataFrame.from_dict(team_preferences, orient='index')
        st.dataframe(df_scores.style.background_gradient(cmap='RdYlGn', axis=1))

    with tab2:
        st.subheader("Simulated Veto Phase")

        # Get Ban Style from filtered data or fallback
        ban_style = "BO1"
        if not filtered_df.empty:
            ban_style = filtered_df.iloc[0]["Ban Style"]

        bans, picks = simulate_veto(team1_sim, team2_sim, team_preferences, ban_style)

        st.write(f"Ban Style used: {ban_style}")
        st.write("Bans:")
        for t, m in bans:
            st.write(f"{t} bans {m}")
        st.write("Picks:")
        for t, m in picks:
            st.write(f"{t} picks {m}")

else:
    st.info("Paste your veto data above to get started.")
