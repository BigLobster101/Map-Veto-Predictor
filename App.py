import streamlit as st
import pandas as pd

st.set_page_config(page_title="R6 Siege Veto Predictor", layout="wide")
st.title("🛡️ Rainbow Six Siege Veto Predictor")

# Step 1: Upload Excel File
uploaded_file = st.file_uploader("📤 Upload your `veto_data.xlsx` file", type=["xlsx"])

# Step 2: Map Pool and Veto Step Weights
map_pool = [
    map_pool = [
    "Bank", "Border", "Chalet", "Clubhouse", "Consulate",
    "Kafe Dostoyevsky", "Lair", "Nighthaven Labs", "Skyscraper"
]

step_weights = {
    "BO1": [-3, -2, -1, -3, -2, -1, 0],
    "BO3": [-3, -2, -1, +3, +2, -3, -2, -1, 0]
}

# Step 3: Preference calculation
def get_team_prefs(df, team, style):
    relevant = df[((df['Team 1'] == team) | (df['Team 2'] == team)) & (df['Ban Style'] == style)]
    weights = step_weights[style]
    scores = {m: 0 for m in map_pool}

    for _, row in relevant.iterrows():
        for i, map_name in enumerate(row[3:]):
            if map_name in scores:
                scores[map_name] += weights[i]
    return dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))

# Step 4: Simulate Veto
def simulate_veto(team1, team2, prefs1, prefs2, style):
    steps = len(step_weights[style])
    pool = map_pool[:]
    bans = []
    turn = True  # True = team1 turn

    for _ in range(steps):
        prefs = prefs1 if turn else prefs2
        for m in prefs:
            if m in pool:
                bans.append((team1 if turn else team2, m))
                pool.remove(m)
                break
        turn = not turn
    return bans

# Step 5: Main App Logic
if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        st.success("✅ File uploaded and loaded!")

        mode = st.selectbox("Select Ban Style", ["BO1", "BO3"])
        sim_type = st.radio("Simulation Mode", ["Team vs Team", "You vs Team"])

        teams = sorted(set(df['Team 1']).union(set(df['Team 2'])))

        if sim_type == "Team vs Team":
            team1 = st.selectbox("Team 1 (starts ban)", teams)
            team2 = st.selectbox("Team 2", teams, index=1)
            if st.button("Simulate Veto"):
                prefs1 = list(get_team_prefs(df, team1, mode).keys())
                prefs2 = list(get_team_prefs(df, team2, mode).keys())
                result = simulate_veto(team1, team2, prefs1, prefs2, mode)

                st.subheader("🧠 Veto Simulation Result:")
                for i, (team, mapname) in enumerate(result):
                    st.markdown(f"**Step {i+1}**: `{team}` bans/picks `{mapname}`")

        else:
            your_team = st.text_input("Your Team Name")
            opp_team = st.selectbox("Opponent Team", teams)
            manual_bans = st.multiselect("Choose your bans (max 3)", map_pool)
            if st.button("Predict Opponent Next Ban/Pick"):
                opp_prefs = list(get_team_prefs(df, opp_team, mode).keys())
                remaining = [m for m in map_pool if m not in manual_bans]
                for m in opp_prefs:
                    if m in remaining:
                        st.subheader("Opponent likely bans/picks:")
                        st.markdown(f"➡️ **{m}**")
                        break
    except Exception as e:
        st.error(f"Error reading file: {e}")
else:
    st.info("📥 Upload your `.xlsx` file to begin.")
