import streamlit as st
import pandas as pd
from io import StringIO
import numpy as np

# Map pool
map_pool = [
    "Bank",
    "Border",
    "Chalet",
    "Clubhouse",
    "Consulate",
    "Kafe Dostoyevsky",
    "Lair",
    "Nighthaven Labs",
    "Skyscraper"
]

st.title("R6 Siege Veto Predictor - Paste Data & Simulate")

# Tabs for Data Input and Simulation
tab1, tab2 = st.tabs(["Data Input & Preview", "Team Map Preferences & Simulation"])

with tab1:
    st.header("Select Teams for Simulation")

    team1_sim = st.text_input("Team 1 (Starts ban) for simulation", value="Team A")
    team2_sim = st.text_input("Team 2 for simulation", value="Team B")

    st.markdown("---")

    st.header("Paste past veto data here")
    st.markdown("""
    **Instructions:**  
    Copy your veto data from Excel or elsewhere, including columns:  
    `Team 1`, `Team 2`, `Ban Style`, `Veto 1`, `Veto 2`, ..., `Veto 9`  
    Paste below as tab-separated or comma-separated text.
    """)

    pasted_data = st.text_area("Paste veto data (include header row)", height=200)

    df = pd.DataFrame()
    if pasted_data:
        try:
            df = pd.read_csv(StringIO(pasted_data), sep="\t")
        except Exception:
            try:
                df = pd.read_csv(StringIO(pasted_data))
            except Exception as e:
                st.error(f"Error reading pasted data: {e}")

    if not df.empty:
        # Clean columns
        df.columns = df.columns.str.strip()

        st.subheader("Pasted Veto Data Preview")
        st.dataframe(df)

    else:
        st.info("Paste your veto data above to see the preview.")

with tab2:
    if df.empty:
        st.warning("Paste veto data first in the 'Data Input & Preview' tab.")
    else:
        # Clean columns again here if needed
        df.columns = df.columns.str.strip()

        # Filter data for selected teams
        filtered_df = df[
            ((df["Team 1"] == team1_sim) & (df["Team 2"] == team2_sim)) |
            ((df["Team 1"] == team2_sim) & (df["Team 2"] == team1_sim))
        ]

        if filtered_df.empty:
            st.warning(f"No data found for matches between {team1_sim} and {team2_sim}.")
        else:
            st.header(f"Team Map Preferences & Ban Simulation: {team1_sim} vs {team2_sim}")

            # Define weights for BO1 and BO3 for 9 veto steps
            # Earlier bans: stronger negative weights
            # Picks: positive weights
            # Floating or unpicked maps: 0 weight (neutral)
            # You can tweak these weights to fit your logic

            BO1_WEIGHTS = [-9, -8, -7, -6, -5, -4, -3, -2, 0]  # Early ban = -9, last map left = 0
            BO3_WEIGHTS = [-5, -4, -3, -2, 2, 3, 4, 5, 0]     # Example weights for BO3 ban/pick order

            def get_weights(ban_style):
                return BO1_WEIGHTS if ban_style.upper() == "BO1" else BO3_WEIGHTS

            # Build preference scores per team per map
            # Score = sum over matches of weighted veto step where map appeared for that team
            # For each row (match), get team-specific weights

            # Initialize dicts to hold cumulative scores
            team_scores = {
                team1_sim: {m: 0 for m in map_pool},
                team2_sim: {m: 0 for m in map_pool},
            }
            team_counts = {
                team1_sim: 0,
                team2_sim: 0,
            }

            # Process each match in filtered data
            for _, row in filtered_df.iterrows():
                weights = get_weights(row["Ban Style"])
                team_counts[row["Team 1"]] += 1
                team_counts[row["Team 2"]] += 1

                # For each veto step
                for i in range(1, 10):
                    map_name = row.get(f"Veto {i}", "")
                    if not map_name or map_name not in map_pool:
                        continue

                    # Team 1 banned/picked at step i => apply weight to Team 1 preference (dislike if negative)
                    if row["Team 1"] in team_scores:
                        team_scores[row["Team 1]][map_name] += weights[i-1]

                    # Team 2 banned/picked at step i => apply weight to Team 2 preference
                    if row["Team 2"] in team_scores:
                        team_scores[row["Team 2]][map_name] += weights[i-1]

            # Convert scores to DataFrame for plotting
            df_scores = pd.DataFrame(team_scores).fillna(0)

            st.subheader("Map Preference Scores")
            st.write("Higher (more positive) score means more preferred by team.")

            # Show bar charts for each team
            for team in [team1_sim, team2_sim]:
                st.markdown(f"### {team}")
                scores = df_scores[team].sort_values(ascending=False)
                st.bar_chart(scores)

            # --- Ban Simulation (simple heuristic) ---

            st.subheader("Simulated Ban Phase")

            # Maps available at start
            available_maps = set(map_pool)

            # Keep track of bans
            bans = []

            # Alternate banning starting with Team 1
            banning_order = [team1_sim, team2_sim] * 4  # max 8 bans possible, for BO3 or BO1

            for banning_team in banning_order:
                # From available maps, ban the map with lowest preference score for banning team
                team_pref = df_scores[banning_team]
                # Filter to only available maps
                team_pref = team_pref.loc[team_pref.index.isin(available_maps)]
                if team_pref.empty:
                    break

                # Map with lowest preference (lowest score)
                ban_map = team_pref.idxmin()
                bans.append((banning_team, ban_map))
                available_maps.remove(ban_map)

                st.write(f"**{banning_team} bans:** {ban_map}")

                # Stop if only 1 map left (decider)
                if len(available_maps) == 1:
                    break

            st.write(f"**Remaining map(s) (potential decider or picks):** {', '.join(available_maps)}")

