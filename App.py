import streamlit as st
import pandas as pd
from io import StringIO

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

# --- Choose teams for simulation ---

st.header("Select Teams for Simulation")

team1_sim = st.text_input("Team 1 (Starts ban) for simulation", value="Team A")
team2_sim = st.text_input("Team 2 for simulation", value="Team B")

st.markdown("---")

# --- Paste veto data ---

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
        # Try reading as CSV with tab separator first (for Excel paste)
        df = pd.read_csv(StringIO(pasted_data), sep="\t")
    except Exception:
        try:
            # Fallback: try comma-separated
            df = pd.read_csv(StringIO(pasted_data))
        except Exception as e:
            st.error(f"Error reading pasted data: {e}")

if not df.empty:
    st.subheader("Pasted Veto Data Preview")
    st.dataframe(df)

    # Filter data for simulation teams only (optional)
    filtered_df = df[(df["Team 1"] == team1_sim) & (df["Team 2"] == team2_sim)]

    st.subheader(f"Filtered Data for {team1_sim} vs {team2_sim}")
    st.dataframe(filtered_df)

    # Here you can add your veto prediction logic using filtered_df

else:
    st.info("Paste your veto data above to see the preview.")

