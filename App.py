import streamlit as st
import pandas as pd

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

# Define expected columns
default_cols = [
    "Team 1", "Team 2", "Ban Style",
    "Veto 1", "Veto 2", "Veto 3", "Veto 4", "Veto 5",
    "Veto 6", "Veto 7", "Veto 8", "Veto 9"
]

# Start with empty DataFrame with these columns
df = pd.DataFrame(columns=default_cols)

# Data editor for easy paste/edit like Excel
edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

# If we have data, clean and validate
if not edited_df.empty:
    # Strip whitespace and normalize case on columns and map names
    edited_df.columns = edited_df.columns.str.strip()
    for col in edited_df.columns:
        if edited_df[col].dtype == object:
            edited_df[col] = edited_df[col].astype(str).str.strip()

    # Normalize Ban Style (uppercase)
    if "Ban Style" in edited_df.columns:
        edited_df["Ban Style"] = edited_df["Ban Style"].str.upper()

    # Normalize map names in veto columns (title case)
    for i in range(1, 10):
        col = f"Veto {i}"
        if col in edited_df.columns:
            edited_df[col] = edited_df[col].str.title()

    # Validate map names
    all_maps = set(pd.unique(edited_df[[f"Veto {i}" for i in range(1,10)]].values.ravel()))
    all_maps.discard('')  # remove empty strings if any
    invalid_maps = all_maps - set(MAP_POOL)
    if invalid_maps:
        st.warning(f"Unknown maps detected in veto columns: {invalid_maps}")

    # Show cleaned preview
    st.subheader("Cleaned Data Preview")
    st.dataframe(edited_df)

    # Choose teams to simulate bans
    team1_sim = st.selectbox("Select Team 1 for Simulation", options=sorted(edited_df["Team 1"].unique()))
    team2_sim = st.selectbox("Select Team 2 for Simulation", options=sorted(edited_df["Team 2"].unique()))

    # Filter data for simulation (you can improve this logic)
    filtered_df = edited_df[(edited_df["Team 1"] == team1_sim) & (edited_df["Team 2"] == team2_sim)]

    st.write(f"Filtered {len(filtered_df)} past veto phases between {team1_sim} and {team2_sim}")

    # TODO: Add your weighted preference calculation and simulation here using 'filtered_df'
    # Example placeholder:
    if len(filtered_df) > 0:
        st.write("Simulation logic placeholder: Compute weighted map preferences and simulate bans here.")
    else:
        st.info("No past data for these teams, simulation will use general preferences or defaults.")

else:
    st.info("Paste your veto data above to get started.")
