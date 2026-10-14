# This code was mainly written by: Jerom den Rooijen. See the commit history for a detailed contribution record.

# Import plotly and steamlit
import plotly.express as px
import streamlit as st 

from python.src.config import (
    ANIMATION, FIGURES, DELIVERABLES,
    SPEED_DISTANCE_MODEL,
    SPEED_DISTANCE_PLOT, SPEED_LANDSCAPE_PLOT, MIXED_RESULTS,
    DAY_NIGHT_PLOT, DAY_NIGHT_MODEL,)

### Dashboard to answer research questions
# General source: https://www.geeksforgeeks.org/python/streamlit-introduction-and-setup/
# General source: https://docs.streamlit.io/develop/api-reference/text/st.title

# Source: https://docs.streamlit.io/develop/api-reference/configuration/st.set_page_config
st.set_page_config(page_title="Caracals in Cape Town", layout="wide")

#Starting page.
def home_page():

    # Title
    st.title("Start: Caracals in Cape Town")
    
    # Main research question.
    st.subheader("Main Research Question: **'To what extend does a medium-sized predator care about human activity?'**")
    
    # Project information
    st.info(":small[Group: gezellig_positive_koffie_zebra]\n\n"
    ":small[Kahsu Berihu Berhe, Joep van Dongen, Jerom den Rooijen, Silke Zeeuwen]\n\n"
    ":small[14-10-2026]\n\n"
    ":small[Geoscripting Final Project, Challenge #5]")
    
    # General explanation of dashboard and its utilities.
    st.markdown(
        "The visualisation will provide an overview of how the animals move through Cape Town (South-Africa) during periods within 2014 and 2017. "
        "To answer the main research question this dashboard will first answer three sub-questions: "
        "navigate through our project, using the menu on the left, to get the answer on the main research question at the end.")

    # Figure 1
    st.iframe(ANIMATION, height=800)

    # Figure 2
    with st.expander("Amount of GPS points per caracal."):
        st.image( 
            FIGURES / "s09a_gps_points_per_caracal.png",
            caption="Amount of GPS points per caracal.",)
        
        st.info(
            "A look into our dataset with gps measurements per caracal. Notice the amount of GPS points are unevenly distrubted per caracal.")

# Page 1
def question_1_page():
    st.title("Q1: Speed and distance to roads")
    
    # Subquestion, info cards: Source: https://docs.streamlit.io/develop/api-reference/status/st.info
    st.info("'Do caracals move at different speeds when they are close to roads compared with when they are farther from roads, potentially indicating a behavioural response to roads?'")
    
    # Figure 3
    with st.expander("Road network within our study area."):
        st.image( 
            FIGURES / "s03a_roads.png",
            caption="Road network within our study area.",
            alt="",)
    
    # Figure 4
    with st.expander("Speed statistics per distance class."):
        st.image( 
            FIGURES / "s13_q1_speed_vs_distance.png",
            caption="Speed statistics per distance class.",
            alt="",)
    
        # Explanation of graphs in figure 4.
        st.info(
            "•	Left graph (boxplots): the typical speed (median) is low and similar in all distance classes.\n\n"
            "•	Right graph (mean speed): caracals are fastest very close to roads (0-10 m, about 0.38 km/h). They are slowest at 50-100 m (about 0.17 km/h) and a bit faster again far away (>500 m, about 0.27 km/h).")

    # Answer of subquestion 1.
    with st.expander("Answer of Q1"):
        st.success("Yes. Caracals move faster when very close to roads. This may mean they hurry near roads.")

# Page 2
def question_2_page():
    st.title("Q2: Urban vs wildland")
    
    st.info("'Does the relationship between movement, speed and distance to roads differ between urban and wildland-dominated areas?'")

    # Figure 5
    with st.expander("Landuse classes within our study area."):
        st.image( 
            FIGURES / "s03b_landuse_classes.png",
            caption="Landuse classes within our study area.",
            alt="",)

    # Figure 6
    with st.expander("Urban versus wildland."):
        st.image( 
            FIGURES / "s13_q2_urban_vs_wildland.png",
            caption="Urban versus wildland.",
            alt="",)
        
        # Explanation of graphs in figure 6.
        st.info(
        "•	Left graph: overall speed is similar in both landscapes.\n\n"
        "•	Middle graph: urban caracals stay much closer to roads (median about 125 m) than wildland caracals (median about 480 m).\n\n"
        "•	Right graph: in urban areas (red line), speed goes up quickly as distance from the road increases. In wildland (green line), speed goes up only a little. The lines cross at about 500 m."
        )

    # Answer of subquestion 2.
    with st.expander("Answer of Q2"):
        st.success("Yes. Road distance affects speed more strongly in urban areas.")

# Page 3
def question_3_page():
    st.title("Q3: Day vs night")

    st.info("'Does the relationship between movement speed and distance to roads differ between daytime and nighttime?'")
    
    # Figure 7
    with st.expander("Influence of day and night time on movement."):
        st.image( 
            FIGURES / "s13_q3_day_vs_night.png",
            caption="Influence of day and night time on movement.",
            alt="",)
        
        st.info("•	Left graph: night speeds are higher than day speeds (median about 0.09 vs. 0.06 km/h (log-scale))\n\n"
        "•	Right graph: at night (blue line), speed rises as distance from the road increases. During the day (orange line) the line is almost flat.")

    # Answer of subquestion 3.
    with st.expander("Answer of Q3"):
        st.success("So, to answer the sub-question:\n\n" 
        "Yes. The effect of distance to the road on speed is observed mainly at night.")

# Ending page
def end_page():

    # Title
    st.title("End: Caracals in Cape Town")

    st.info("Main Research Question: **'To what extend does a medium-sized predator care about human activity?'**")
    
    st.success("In this project, Caracals were found to move faster near roads, stay closer to roads in urban areas and show a stronger relationship between road distance and movement speed at night, compared with daytime observations. These findings do not indicate complete avoidance of human activity. Rather, they suggest behavioural adjustment. Faster movement near roads could mean that Caracals use roads to travel more efficiently. Their slower movement speeds in urban areas could be a sign of more cautious movement behaviour. Furthermore, avoidance of roads at night could indicate the repelling effect of bright car lights. However, these potential explanations cannot be scientifically supported by the current analyses.")


# Navigation through pages s: https://docs.streamlit.io/develop/api-reference/navigation/st.page for icons https://fonts.google.com/icons
pg = st.navigation([
    st.Page(home_page, title="Main Research Question", icon=":material/map:", default=True),
    st.Page(question_1_page, title="Q1 Speed vs Distance", icon=":material/speed:"),
    st.Page(question_2_page, title="Q2 Urban vs Wildland", icon=":material/location_city:"),
    st.Page(question_3_page, title="Q3 Day vs Night", icon=":material/dark_mode:"),
    st.Page(end_page, title="Conclusion", icon=":material/sports_score:"), ])
pg.run()



