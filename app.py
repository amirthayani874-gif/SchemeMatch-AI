import streamlit as st
import pandas as pd


from pathlib import Path
from modules.translations import init_language
from modules.database import initialize_database
from modules.notifications import run_notification_check


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="SchemeMatch AI",
    page_icon="🎯",
    layout="wide"
)

st.markdown(
    """
    <style>
        /* Make the entire application wide */
        .block-container {
            max-width: 95% !important;
            padding-left: 3rem !important;
            padding-right: 3rem !important;
            padding-top: 2rem !important;
            padding-bottom: 3rem !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

initialize_database()

BASE_DIR = Path(__file__).resolve().parent

schemes = pd.read_csv(
    BASE_DIR / "data" / "schemes.csv"
)

run_notification_check(schemes)


# --------------------------------------------------
# INITIALIZE GLOBAL LANGUAGE
# --------------------------------------------------

init_language()


# --------------------------------------------------
# DEFINE PAGES
# --------------------------------------------------

home = st.Page(
    "home.py",
    title="Home",
    icon="🏠"
)

find_schemes = st.Page(
    "pages/1_Find_Schemes.py",
    title="Find My Schemes",
    icon="🎯"
)

compare_schemes = st.Page(
    "pages/3_Compare.py",
    title="Compare Schemes",
    icon="⚖️"
)

ai_assistant = st.Page(
    "pages/2_AI_Assistant.py",
    title="AI Assistant",
    icon="🤖"
)

notifications = st.Page(
    "pages/4_Notifications.py",
    title="Notifications",
    icon="🔔"
)

profiles = st.Page(
    "pages/5_Profiles.py",
    title="Stored Profiles",
    icon="👤"
)

document_readiness = st.Page(
    "pages/6_Document_Readiness.py",
    title="Document Readiness",
    icon="📄"
)

# --------------------------------------------------
# NAVIGATION
# --------------------------------------------------

pg = st.navigation(
    [
        home,
        find_schemes,
        profiles,
        compare_schemes,
        ai_assistant,
        notifications,
        document_readiness
    ],
    position="hidden"
)


# --------------------------------------------------
# RUN CURRENT PAGE
# --------------------------------------------------

pg.run()