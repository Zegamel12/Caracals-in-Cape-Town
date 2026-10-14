# Import plotly and steamlit
import plotly.express as px
import streamlit as st 
# General source: https://www.geeksforgeeks.org/python/streamlit-introduction-and-setup/
# General source: https://docs.streamlit.io/develop/api-reference/text/st.title
from python.src.config import ANIMATION, FIGURES, DELIVERABLES

# Source: https://docs.streamlit.io/develop/api-reference/configuration/st.set_page_config
st.set_page_config(page_title="Caracals in Cape Town", layout="wide")

def home_page():

    # Title
    st.title("Caracals in Cape Town")
    # Import title card animation map
    st.iframe(ANIMATION, height=800)

def question_1_page():
    st.title("Q1: Speed and distance to roads")
    st.image(FIGURES / "s13_q1_speed_vs_distance.png", caption="Speed vs distance to the nearest road")
    st.iframe(FIGURES / "s09e_speed_vs_distance.html", height=800)

def question_2_page():
    st.title("Q2: Urban vs wildland")
    st.image(FIGURES / "s03b_landuse_classes.png", caption="OSM land-use classes")
    st.image(FIGURES / "s13_q2_urban_vs_wildland.png", caption="Urban vs wildland")

def question_3_page():
    st.title("Q3: Day vs night")
    st.image(FIGURES / "s13_q3_day_vs_night.png", caption="Day vs night")

# Navigation s: https://docs.streamlit.io/develop/api-reference/navigation/st.page for icons https://fonts.google.com/icons
pg = st.navigation([
    st.Page(home_page, title="Animal movements", icon=":material/map:", default=True),
    st.Page(question_1_page, title="Q1 Speed vs distance", icon=":material/speed:"),
    st.Page(question_2_page, title="Q2 Urban vs wildland", icon=":material/location_city:"),
    st.Page(question_3_page, title="Q3 Day vs night", icon=":material/dark_mode:"), ])
pg.run()