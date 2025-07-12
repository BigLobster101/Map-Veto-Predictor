import streamlit as st
import pandas as pd

# Load Excel
@st.cache_data
def load_data():
    df = pd.read_excel("veto_data.xlsx")
    return df

df = load_data()

st.title("Rainbow Six Siege Map Veto Predictor")

mode = st.selectbox("Select Veto Mode", ["BO1", "BO3"])
simulation_type = st.radio("Simulation Type", ["Team vs Team", "You vs Team"])

map_pool = [
    "Bank", "Oregon", "Clubhouse", "Chalet", "Kafe", "Theme Park",
    "Skyscraper", "Consulate", "Border"
]

step_weights = {
    "BO1": [-3, -2, -1, -3, -2, -1, 0],
    "BO3": [-3, -2, -1, +3, +2, -3, -2, -1, 0]
}

def get_team_prefs(df, team, style):
    relevant = df[((df['Team 1'] == team) | (df['Team 2'] == team)) & (df['Ban Style'] == style)]
    weights = step_weights[style]
    scores = {m: 0 for m in map_pool}

    for _, row in relevant.iterrows():
        for i, map_name in enumerate(row[3:]):
            if map_name in scores:
                scores[map_name] += weights[i]
    
    return dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))

def simulate_veto(team1, team2, prefs1, prefs2, style):
    steps = 7 if style == "BO1" else 9
    pool = map_pool[:]
    bans = []
    turn = True  # True = team1

    for _ in range(steps):
        prefs = prefs1 if turn else prefs2
        for m in prefs:
            if m in pool:
                bans.append((team1 if turn else team2, m))
                pool.remove(m)
                break
        turn = not turn
    return bans

# UI Logic
if simulation_type == "Team vs Team":
    team_list = sorted(df['Team 1'].unique())
    team_a = st.selectbox("Team A (starts ban)", team_list)
    team_b = st.selectbox("Team B", team_list)

    if st.button("Simulate Ban Phase"):
        prefs_a = list(get_team_prefs(df, team_a, mode).keys())
        prefs_b = list(get_team_prefs(df, team_b, mode).keys())
        result = simulate_veto(team_a, team_b, prefs_a, prefs_b, mode)

        st.subheader("Ban Sequence:")
        for i, (team, map_name) in enumerate(result):
            st.write(f"Step {i+1}: {team} bans/picks {map_name}")

elif simulation_type == "You vs Team":
    your_team = st.text_input("Your Team Name")
    opp_team = st.selectbox("Opponent Team", sorted(df['Team 1'].unique()))
    user_bans = st.multiselect("Choose your bans", map_pool, max_selections=3)

    if st.button("Simulate Opponent Response"):
        remaining = [m for m in map_pool if m not in user_bans]
        opp_prefs = list(get_team_prefs(df, opp_team, mode).keys())
        for m in opp_prefs:
            if m in remaining:
                st.write(f"Opponent likely bans/picks: **{m}**")
                break

