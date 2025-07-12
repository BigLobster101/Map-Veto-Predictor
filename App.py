import streamlit as st
import pandas as pd

st.set_page_config(page_title="R6 Siege Veto Predictor", layout="wide")
st.title("🛡️ Rainbow Six Siege Veto Predictor")

# Map pool as you provided
map_pool = [
    "Bank", "Border", "Chalet", "Clubhouse", "Consulate",
    "Kafe Dostoyevsky", "Lair", "Nighthaven Labs", "Skyscraper"
]

# Step weights for veto positions (can tweak later)
step_weights = {
    "BO1": [-3, -2, -1, -3, -2, -1, 0],
    "BO3": [-3, -2, -1, +3, +2, -3, -2, -1, 0]
}

# File uploader
uploaded_file = st.file_uploader("📤 Upload your veto_data.xlsx file", type=["xlsx"])

def get_team_prefs(df, team, style):
    # Filter matches involving the team and the ban style
    relevant = df[((df['Team 1'] == team) | (df['Team 2'] == team)) & (df['Ban Style'] == style)]
    weights = step_weights[style]
    scores = {m: 0 for m in map_pool}

    for _, row in relevant.iterrows():
        # Iterate over the 9 veto steps (starting at 4th column, zero-based idx = 3)
        for i, map_name in enumerate(row[3:12]):  # Columns 4-12 are the veto steps
            if map_name in scores:
                scores[map_name] += weights[i]
    # Sort by descending score to get preferences
    return dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))

def simulate_veto(team1, team2, prefs1, prefs2, style):
    steps = len(step_weights[style])
    pool = map_pool[:]
    bans = []
    turn = True  # True = team1 turn, False = team2

    for _ in range(steps):
        prefs = prefs1 if turn else prefs2
        for m in prefs:
            if m in pool:
                bans.append((team1 if turn else team2, m))
                pool.remove(m)
                break
        turn = not turn
    return bans

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        st.success("✅ File uploaded and loaded!")

        # Validate that your Excel has the required columns:
        required_cols = ['Team 1', 'Team 2', 'Ban Style']
        if not all(col in df.columns for col in required_cols):
            st.error(f"Excel file must contain columns: {required_cols}")
        else:
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
    st.info("📥 Upload your `.xlsx` veto data file to begin.")
