import streamlit as st
import pandas as pd

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

st.title("R6 Siege Veto Predictor - Manual Data Entry")

# --- Manual data entry ---

st.header("Enter past veto data manually")

num_rows = st.number_input("How many past matches to enter?", min_value=1, max_value=20, value=3)

data = {
    "Team 1": [],
    "Team 2": [],
    "Ban Style": [],
}

for i in range(1, 10):
    data[f"Veto {i}"] = []

for row_idx in range(num_rows):
    st.markdown(f"### Match #{row_idx+1}")
    team1 = st.text_input(f"Team 1 (Starts ban) [{row_idx+1}]", key=f"team1_{row_idx}")
    team2 = st.text_input(f"Team 2 [{row_idx+1}]", key=f"team2_{row_idx}")
    ban_style = st.selectbox(f"Ban Style [{row_idx+1}]", options=["BO1", "BO3"], key=f"banstyle_{row_idx}")

    vetoes = []
    for i in range(1, 10):
        veto = st.selectbox(f"Veto {i} [{row_idx+1}]", options=[""] + map_pool, key=f"veto_{i}_{row_idx}")
        vetoes.append(veto)

    data["Team 1"].append(team1)
    data["Team 2"].append(team2)
    data["Ban Style"].append(ban_style)
    for i in range(1, 10):
        data[f"Veto {i}"].append(vetoes[i-1])

df = pd.DataFrame(data)

st.subheader("Entered Veto Data")
st.dataframe(df)

# ---- Here you add your veto prediction / simulation logic using 'df' as your data source ----
# Example placeholder:
st.info("Now use the entered data for predictions or simulations!")

