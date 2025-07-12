import streamlit as st
import pandas as pd
from veto_logic import predict_veto_order
from map_data import get_maps

st.set_page_config(page_title="Map Veto Predictor", layout="wide")

st.title("🗺️ Map Veto Predictor")

team1 = st.text_input("Team 1 (starts veto)", "Team A")
team2 = st.text_input("Team 2", "Team B")
ban_style = st.selectbox("Ban Style", ["BO1", "BO3"])

maps = get_maps()

st.subheader("Available Maps")
st.write(maps)

if st.button("Predict Veto Order"):
    predicted = predict_veto_order(team1, team2, ban_style, maps)
    st.subheader("Predicted Veto Order")
    st.dataframe(predicted)
