import streamlit as st

from modules.translations import (
    render_language_selector,
    t
)

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="SchemeMatch AI",
    page_icon="🎯",
    layout="wide"
)

# --------------------------------------------------
# GLOBAL LANGUAGE SELECTOR
# --------------------------------------------------

# --------------------------------------------------
# LANGUAGE + PROFILE HEADER
# --------------------------------------------------

lang_col, profile_col = st.columns([6, 1.2], gap="medium")

with lang_col:
    render_language_selector()

with profile_col:
    st.markdown(
        "<div style='height: 28px;'></div>",
        unsafe_allow_html=True
    )

    if st.button(
        "👤 Profiles",
        key="profiles_top_btn",
        use_container_width=True
    ):
        st.switch_page("pages/5_Profiles.py")

        
# --------------------------------------------------
# MODERN UI STYLING
# --------------------------------------------------

st.markdown(
    """
<style>

/* Main Container Constraint */
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2.5rem;
    max-width: 1040px;
}

/* Small Stored Profiles Button */
div.stButton > button[kind="secondary"] {
    white-space: nowrap;
}

/* Modern Gradient Hero Header */
.hero-box {
    padding: 2.5rem 2rem;
    border-radius: 20px;
    background: linear-gradient(135deg, #4f46e5 0%, #3730a3 100%);
    color: #ffffff;
    text-align: center;
    box-shadow: 0 10px 25px -5px rgba(79, 70, 229, 0.3);
    margin-bottom: 2rem;
}

.hero-title {
    font-size: 2.6rem;
    font-weight: 800;
    margin-bottom: 0.6rem;
    letter-spacing: -0.02em;
    color: #ffffff;
}

.hero-text {
    font-size: 1.1rem;
    color: #e0e7ff;
    max-width: 750px;
    margin: 0 auto;
    line-height: 1.6;
}

/* Streamlit Container Card Customization */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #ffffff;
    border: 1px solid #e2e8f0 !important;
    border-radius: 16px !important;
    padding: 1.25rem !important;
    transition: all 0.25s ease-in-out;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
}

div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    transform: translateY(-4px);
    border-color: #c7d2fe !important;
    box-shadow: 0 12px 24px -4px rgba(79, 70, 229, 0.12);
}

/* Card Header & Content Layout */
.card-header-row {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 0.8rem;
}

.card-icon-badge {
    font-size: 1.4rem;
    background: #f1f5f9;
    width: 44px;
    height: 44px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.card-title-text {
    font-size: 1.25rem;
    font-weight: 700;
    color: #0f172a;
    margin: 0;
    line-height: 1.3;
}

.card-body-text {
    color: #64748b;
    font-size: 0.95rem;
    line-height: 1.6;
    margin-bottom: 1.2rem;
    min-height: 60px;
}

/* Action Buttons Styling */
div.stButton > button {
    border-radius: 10px !important;
    height: 2.85rem !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    border: 1px solid #cbd5e1 !important;
    background-color: #f8fafc !important;
    color: #1e293b !important;
    transition: all 0.2s ease !important;
}

div.stButton > button:hover {
    border-color: #4f46e5 !important;
    color: #4f46e5 !important;
    background-color: #eef2ff !important;
}

/* Primary Accent Button for 'Find My Schemes' */
div[key="find_schemes_btn"] > button {
    background: linear-gradient(135deg, #4f46e5, #4338ca) !important;
    color: #ffffff !important;
    border: none !important;
}

div[key="find_schemes_btn"] > button:hover {
    background: linear-gradient(135deg, #4338ca, #3730a3) !important;
    color: #ffffff !important;
    box-shadow: 0 6px 14px rgba(79, 70, 229, 0.3) !important;
}

/* Disclaimer Styling */
.disclaimer-card {
    margin-top: 2rem;
    padding: 1.1rem 1.3rem;
    border-radius: 14px;
    background-color: #fffbe6;
    border: 1px solid #ffe58f;
    color: #714b00;
    font-size: 0.92rem;
    line-height: 1.5;
    display: flex;
    align-items: center;
    gap: 10px;
}

</style>
""",
    unsafe_allow_html=True
)

# --------------------------------------------------
# HERO SECTION
# --------------------------------------------------

st.markdown(
    f"""
<div class="hero-box">
    <div class="hero-title">🎯 {t("app_title")}</div>
    <div class="hero-text">{t("home_subtitle")}</div>
</div>
""",
    unsafe_allow_html=True
)

# --------------------------------------------------
# ROW 1: FIND MY SCHEMES + AI ASSISTANT
# --------------------------------------------------

col1, col2 = st.columns(2, gap="medium")

with col1:
    with st.container(border=True):
        st.markdown(
            f"""
        <div class="card-header-row">
            <div class="card-icon-badge">🔎</div>
            <h3 class="card-title-text">{t("find_schemes")}</h3>
        </div>
        <div class="card-body-text">
            {t("find_schemes_description")}
        </div>
        """,
            unsafe_allow_html=True
        )

        if st.button(
            t("find_schemes"),
            use_container_width=True,
            key="find_schemes_btn"
        ):
            st.switch_page("pages/1_Find_Schemes.py")

with col2:
    with st.container(border=True):
        st.markdown(
            f"""
        <div class="card-header-row">
            <div class="card-icon-badge">🤖</div>
            <h3 class="card-title-text">{t("ai_assistant")}</h3>
        </div>
        <div class="card-body-text">
            {t("ai_assistant_description")}
        </div>
        """,
            unsafe_allow_html=True
        )

        if st.button(
            f"💬 {t('ai_assistant')}",
            use_container_width=True,
            key="ai_assistant_btn"
        ):
            st.switch_page("pages/2_AI_Assistant.py")

# --------------------------------------------------
# SPACE BETWEEN ROWS
# --------------------------------------------------

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

# --------------------------------------------------
# ROW 2: COMPARE SCHEMES + NOTIFICATIONS
# --------------------------------------------------

col3, col4 = st.columns(2, gap="medium")

with col3:
    with st.container(border=True):
        st.markdown(
            f"""
        <div class="card-header-row">
            <div class="card-icon-badge">⚖️</div>
            <h3 class="card-title-text">{t("compare_schemes")}</h3>
        </div>
        <div class="card-body-text">
            {t("compare_schemes_description")}
        </div>
        """,
            unsafe_allow_html=True
        )

        if st.button(
            f"⚖️ {t('compare_schemes')}",
            use_container_width=True,
            key="compare_schemes_btn"
        ):
            st.switch_page("pages/3_Compare.py")

with col4:
    with st.container(border=True):
        st.markdown(
            f"""
        <div class="card-header-row">
            <div class="card-icon-badge">🔔</div>
            <h3 class="card-title-text">{t("notifications")}</h3>
        </div>
        <div class="card-body-text">
            {t("notifications_description")}
        </div>
        """,
            unsafe_allow_html=True
        )

        if st.button(
            f"🔔 {t('notifications')}",
            use_container_width=True,
            key="notifications_btn"
        ):
            st.switch_page("pages/4_Notifications.py")

# --------------------------------------------------
# DISCLAIMER
# --------------------------------------------------

st.markdown(
    f"""
<div class="disclaimer-card">
    <span>⚠️</span>
    <div>{t("disclaimer")}</div>
</div>
""",
    unsafe_allow_html=True
)