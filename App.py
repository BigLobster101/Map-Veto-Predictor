import streamlit as st
import pandas as pd
from io import StringIO

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

tab1, tab2 = st.tabs(["Data Input & Preview", "Team Map Preferences & Simulation"])

with tab1:
    st.header("Paste past veto data")
    st.markdown("""
    Paste veto data including columns:  
    `Team 1`, `Team 2`, `Ban Style`, `Veto 1` to `Veto 9`  
    Copy from Excel or elsewhere as tab or comma separated text.
    """)
    pasted_data = st.text_area("Paste veto data here (include header)", height=200)

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
        df.columns = df.columns.str.strip()
        st.subheader("Data Preview")
        st.dataframe(df)
    else:
        st.info("Paste veto data above to preview.")

with tab2:
    if df.empty:
        st.warning("Paste veto data first in the 'Data Input & Preview' tab.")
    else:
        df.columns = df.columns.str.strip()

        # Input for sim teams
        team1_sim = st.text_input("Team 1 for simulation", value="Team A")
        team2_sim = st.text_input("Team 2 for simulation", value="Team B")

        # Define weights for BO1 and BO3
        BO1_WEIGHTS = [-9, -8, -7, -6, -5, -4, -3, -2, 0]
        BO3_WEIGHTS = [-5, -4, -3, -2, 2, 3, 4, 5, 0]

        def get_weights(ban_style):
            return BO1_WEIGHTS if ban_style.upper() == "BO1" else BO3_WEIGHTS

        # Calculate global preference scores per team and map
        team_map_scores = {}
        team_game_counts = {}

        # Initialize teams found in data
        all_teams = pd.unique(df[['Team 1', 'Team 2']].values.ravel())

        for team in all_teams:
            team_map_scores[team] = {m: 0 for m in map_pool}
            team_game_counts[team] = 0

        # Process every row to accumulate scores per team
        for _, row in df.iterrows():
            weights = get_weights(row["Ban Style"])
            # Each team in this row played a game
            for team in [row["Team 1"], row["Team 2"]]:
                team_game_counts[team] += 1

            # For each veto step, assign weighted scores to both teams for the banned/picked map
            for i in range(1, 10):
                map_name = row.get(f"Veto {i}", "")
                if map_name not in map_pool:
                    continue
                # Both teams get score updated (assuming both care about ban order)
                team_map_scores[row["Team 1"]][map_name] += weights[i-1]
                team_map_scores[row["Team 2"]][map_name] += weights[i-1]

        # Normalize scores by number of games played per team to get averages
        for team in team_map_scores:
            count = team_game_counts.get(team, 1)
            if count > 0:
                for map_name in team_map_scores[team]:
                    team_map_scores[team][map_name] /= count

        # Convert to DataFrame for easier use
        df_scores = pd.DataFrame(team_map_scores).fillna(0)

        st.header(f"Map Preferences and Ban Simulation: {team1_sim} vs {team2_sim}")

        # Show preference charts for both teams
        for team in [team1_sim, team2_sim]:
            if team not in df_scores.columns:
                st.warning(f"No data for team '{team}', showing zero preferences.")
                scores = pd.Series([0]*len(map_pool), index=map_pool)
            else:
                scores = df_scores[team]

            st.subheader(f"{team} Map Preferences (average weighted score)")
            st.bar_chart(scores.sort_values(ascending=False))

        st.subheader("Simulated Ban Phase")

        # Start with full map pool available
        available_maps = set(map_pool)
        bans = []

        banning_order = [team1_sim, team2_sim] * 4  # alternate bans max 8 bans

        for banning_team in banning_order:
            if banning_team not in df_scores.columns:
                # No data for this team, ban random map
                ban_map = sorted(available_maps)[0]
            else:
                team_pref = df_scores[banning_team].loc[df_scores.index.isin(available_maps)]
                # Ban the map with lowest preference score (least liked)
                ban_map = team_pref.idxmin()

            bans.append((banning_team, ban_map))
            available_maps.remove(ban_map)

            st.write(f"**{banning_team} bans:** {ban_map}")

            if len(available_maps) == 1:
                break

        st.write(f"**Remaining map(s):** {', '.join(available_maps)}")
