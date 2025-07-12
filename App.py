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

        team1_sim = st.text_input("Team 1 for simulation", value="Team A")
        team2_sim = st.text_input("Team 2 for simulation", value="Team B")

        ban_style = st.selectbox("Ban Style", options=["BO1", "BO3"], index=0)

        BO1_WEIGHTS = [-9, -8, -7, -6, -5, -4, -3, -2, 0]
        BO3_WEIGHTS = [-5, -4, -3, -2, 2, 3, 4, 5, 0]

        def get_weights(ban_style):
            return BO1_WEIGHTS if ban_style.upper() == "BO1" else BO3_WEIGHTS

        weights = get_weights(ban_style)

        # Initialize data structures
        team_map_scores = {}
        team_game_counts = {}

        all_teams = pd.unique(df[['Team 1', 'Team 2']].values.ravel())

        for team in all_teams:
            team_map_scores[team] = {m: 0 for m in map_pool}
            team_game_counts[team] = 0

        # Accumulate weighted scores for each map per team
        for _, row in df.iterrows():
            row_weights = get_weights(row["Ban Style"])
            # Both teams played this match
            for team in [row["Team 1"], row["Team 2"]]:
                team_game_counts[team] += 1
            for i in range(1, 10):
                map_name = row.get(f"Veto {i}", "")
                if map_name not in map_pool:
                    continue
                # Add weight for both teams for this veto step map
                team_map_scores[row["Team 1"]][map_name] += row_weights[i-1]
                team_map_scores[row["Team 2"]][map_name] += row_weights[i-1]

        # Calculate average weighted preference per map per team
        for team in team_map_scores:
            count = team_game_counts.get(team, 1)
            if count > 0:
                for map_name in team_map_scores[team]:
                    team_map_scores[team][map_name] /= count

        df_scores = pd.DataFrame(team_map_scores).fillna(0)

        st.header(f"Map Preferences and Ban Simulation: {team1_sim} vs {team2_sim}")

        # Show bar charts with scores for both teams
        for team in [team1_sim, team2_sim]:
            if team not in df_scores.columns:
                st.warning(f"No data for team '{team}', showing zeros.")
                scores = pd.Series([0]*len(map_pool), index=map_pool)
            else:
                scores = df_scores[team]

            st.subheader(f"{team} Map Preferences (avg weighted score)")
            st.bar_chart(scores.sort_values(ascending=False))

            # Show the raw preference values for debugging
            st.write(scores.sort_values(ascending=False))

        st.subheader("Simulated Ban Phase")

        available_maps = set(map_pool)
        bans = []

        banning_order = [team1_sim, team2_sim] * 4  # up to 8 bans alternating

        for banning_team in banning_order:
            if banning_team not in df_scores.columns:
                # No data, ban lowest alphabetically
                ban_map = sorted(available_maps)[0]
                st.write(f"Warning: No data for {banning_team}, banning {ban_map} randomly")
            else:
                team_pref = df_scores[banning_team].loc[df_scores.index.isin(available_maps)]
                ban_map = team_pref.idxmin()  # ban the map with lowest score

            bans.append((banning_team, ban_map))
            available_maps.remove(ban_map)

            st.write(f"**{banning_team} bans:** {ban_map}")

            if len(available_maps) == 1:
                break

        st.write(f"**Remaining map(s):** {', '.join(available_maps)}")
