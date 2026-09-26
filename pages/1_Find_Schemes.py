import streamlit as st
import pandas as pd
from pathlib import Path

from modules.matching import match_schemes
from modules.database import create_profile, get_profile
from modules.translations import (
    render_language_selector,
    t,
    opt,
    scheme_text
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Find Schemes | SchemeMatch AI",
    page_icon="🎯",
    layout="wide"
)


# ============================================================
# SESSION STATE
# ============================================================

if "results" not in st.session_state:
    st.session_state["results"] = []

if "all_results" not in st.session_state:
    st.session_state["all_results"] = []

if "profile" not in st.session_state:
    st.session_state["profile"] = None

if "profile_id" not in st.session_state:
    st.session_state["profile_id"] = None


# ============================================================
# LANGUAGE
# ============================================================

render_language_selector()


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    .page-header {
        padding: 2rem;
        border-radius: 18px;
        background: linear-gradient(
            135deg,
            #f5f7ff,
            #eef4ff
        );
        border: 1px solid #e2e7f5;
        margin-bottom: 2rem;
    }

    .page-title {
        font-size: 2.3rem;
        font-weight: 700;
        color: #202638;
    }

    .section-title {
        font-size: 1.45rem;
        font-weight: 650;
        color: #202638;
        margin-top: 1rem;
        margin-bottom: 0.35rem;
    }

    .section-description {
        color: #606b80;
        margin-bottom: 1rem;
    }

    .profile-box {
        padding: 1.4rem;
        border: 1px solid #e3e6ed;
        border-radius: 14px;
        background: #ffffff;
        min-height: 280px;
    }

    .profile-label {
        font-size: 0.82rem;
        color: #737d91;
        margin-top: 0.7rem;
        margin-bottom: 0.15rem;
    }

    .profile-value {
        font-size: 1rem;
        font-weight: 600;
        color: #202638;
        margin-bottom: 0.3rem;
    }

    .scheme-title {
        font-size: 1.25rem;
        font-weight: 650;
        color: #202638;
        margin-bottom: 1rem;
    }

    .benefit-label {
        font-size: 0.82rem;
        color: #737d91;
        margin-bottom: 0.2rem;
    }

    .benefit-value {
        font-size: 1.05rem;
        font-weight: 650;
        color: #202638;
        margin-bottom: 0.5rem;
    }

    .top-match {
        display: inline-block;
        padding: 0.35rem 0.75rem;
        border-radius: 20px;
        background: #fff3cd;
        color: #6b5710;
        font-size: 0.82rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
    }

    .document-box {
        padding: 1.2rem 1.4rem;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        background: #f8fafc;
        margin-top: 1.5rem;
    }

    .document-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #202638;
        margin-bottom: 0.25rem;
    }

    .document-description {
        color: #64748b;
        font-size: 0.92rem;
        margin-bottom: 0;
    }

    .disclaimer {
        margin-top: 2rem;
        padding: 1rem 1.2rem;
        border-radius: 10px;
        background: #fff8e6;
        border: 1px solid #f1dfaa;
        color: #66551f;
        font-size: 0.9rem;
        line-height: 1.5;
    }

    .stButton > button {
        border-radius: 10px;
        height: 3rem;
        font-weight: 600;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# LOAD SCHEMES
# ============================================================

@st.cache_data
def load_schemes():

    base_dir = Path(__file__).resolve().parent.parent

    csv_path = base_dir / "data" / "schemes.csv"

    return pd.read_csv(csv_path)


schemes = load_schemes()


# ============================================================
# LOAD SELECTED STORED PROFILE
# ============================================================

selected_profile_id = st.session_state.get(
    "selected_profile_id"
)

stored_profile = None

if selected_profile_id is not None:

    stored_profile = get_profile(
        selected_profile_id
    )

    # --------------------------------------------------------
    # Convert SQLite tuple to dictionary
    # --------------------------------------------------------

    if stored_profile is not None:

        stored_profile = {
            "id": stored_profile[0],
            "name": stored_profile[1],
            "age": stored_profile[2],
            "state": stored_profile[3],
            "district": stored_profile[4],
            "category": stored_profile[5],
            "business_type": stored_profile[6],
            "business_stage": stored_profile[7],
            "annual_income": stored_profile[8],
            "investment": stored_profile[9],
            "employees": stored_profile[10]
        }

    else:

        # Selected profile no longer exists
        st.session_state.pop(
            "selected_profile_id",
            None
        )

        selected_profile_id = None


# ============================================================
# PAGE HEADER
# ============================================================

st.markdown(
    f"""
    <div class="page-header">
        <div class="page-title">
            {t("find_page_title")}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# AUTOMATICALLY LOAD STORED PROFILE
# ============================================================

if (
    selected_profile_id is not None
    and stored_profile is not None
):

    results = match_schemes(
        schemes=schemes,
        age=stored_profile["age"],
        business_type=stored_profile["business_type"],
        business_stage=stored_profile["business_stage"],
        investment_required=stored_profile["investment"],
        target_category=stored_profile["category"],
        state=stored_profile["state"]
    )

    st.session_state["all_results"] = results
    st.session_state["results"] = results[:3]

    st.session_state["profile"] = {
        "id": stored_profile["id"],
        "name": stored_profile["name"],
        "age": stored_profile["age"],
        "state": stored_profile["state"],
        "district": stored_profile["district"],
        "target_category": stored_profile["category"],
        "business_type": stored_profile["business_type"],
        "business_stage": stored_profile["business_stage"],
        "annual_income": stored_profile["annual_income"],
        "investment_required": stored_profile["investment"],
        "employees": stored_profile["employees"]
    }

    st.session_state["profile_id"] = (
        stored_profile["id"]
    )


# ============================================================
# NEW PROFILE FORM
# ============================================================

if selected_profile_id is None:

    st.markdown(
        f"""
        <div class="section-title">
            {t("entrepreneur_profile")}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="section-description">
            {t("profile_description")}
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(
        2,
        gap="large"
    )

    # ========================================================
    # BASIC DETAILS
    # ========================================================

    with col1:

        name = st.text_input(
            t("name"),
            placeholder=t("name_placeholder")
        )

        age = st.number_input(
            t("age"),
            min_value=18,
            max_value=100,
            value=25
        )

        state_options = [
            "Tamil Nadu",
            "Kerala",
            "Karnataka",
            "Andhra Pradesh",
            "Telangana",
            "Maharashtra",
            "Other"
        ]

        state = st.selectbox(
            t("state"),
            state_options,
            format_func=opt
        )

        district = st.text_input(
            t("district"),
            placeholder=t("district_placeholder")
        )

        category_options = [
            "General",
            "Women Entrepreneur",
            "SC",
            "ST",
            "OBC",
            "Minority",
            "Person with Disability",
            "Artisan",
            "Craftsperson",
            "Other"
        ]

        target_category = st.selectbox(
            t("category"),
            category_options,
            format_func=opt
        )

    # ========================================================
    # BUSINESS DETAILS
    # ========================================================

    with col2:

        business_type_options = [
            "Agriculture",
            "Food Processing",
            "Manufacturing",
            "Retail",
            "Textile",
            "Handicrafts",
            "Technology / IT",
            "Services",
            "Education",
            "Healthcare",
            "Other"
        ]

        business_type = st.selectbox(
            t("business_type"),
            business_type_options,
            format_func=opt
        )

        business_stage_options = [
            "Business Idea",
            "Starting a New Business",
            "Existing Business",
            "Business Expansion"
        ]

        business_stage = st.selectbox(
            t("business_stage"),
            business_stage_options,
            format_func=opt
        )

        annual_income = st.number_input(
            t("annual_income"),
            min_value=0,
            value=250000,
            step=10000
        )

        investment_required = st.number_input(
            t("investment"),
            min_value=0,
            value=500000,
            step=10000
        )

        employees = st.number_input(
            t("employees"),
            min_value=0,
            max_value=10000,
            value=2
        )

    # ========================================================
    # FIND BUTTON
    # ========================================================

    if st.button(
        t("find_button"),
        use_container_width=True
    ):

        if not name.strip():

            st.warning(
                f"⚠️ {t('name')}"
            )

            st.stop()

        if not district.strip():

            st.warning(
                f"⚠️ {t('district')}"
            )

            st.stop()

        # ----------------------------------------------------
        # CREATE PROFILE
        # ----------------------------------------------------

        profile_id = create_profile(
            name=name,
            age=age,
            state=state,
            district=district,
            category=target_category,
            business_type=business_type,
            business_stage=business_stage,
            annual_income=annual_income,
            investment=investment_required,
            employees=employees
        )

        profile = {
            "id": profile_id,
            "name": name,
            "age": age,
            "state": state,
            "district": district,
            "target_category": target_category,
            "business_type": business_type,
            "business_stage": business_stage,
            "annual_income": annual_income,
            "investment_required": investment_required,
            "employees": employees
        }

        st.session_state["profile"] = profile
        st.session_state["profile_id"] = profile_id

        # ----------------------------------------------------
        # MATCH SCHEMES
        # ----------------------------------------------------

        results = match_schemes(
            schemes=schemes,
            age=age,
            business_type=business_type,
            business_stage=business_stage,
            investment_required=investment_required,
            target_category=target_category,
            state=state
        )

        st.session_state["all_results"] = results
        st.session_state["results"] = results[:3]

        st.success(
            f"{t('profile_created')} **{name}**! 🎉"
        )

        st.rerun()


# ============================================================
# DISPLAY PROFILE + RESULTS
# ============================================================

profile = st.session_state.get("profile")

if profile is not None:

    results = st.session_state.get(
        "results",
        []
    )

    # ========================================================
    # PROFILE
    # ========================================================

    st.divider()

    st.markdown(
        f"""
        <div class="section-title">
            {t("your_profile")}
        </div>
        """,
        unsafe_allow_html=True
    )

    profile_col1, profile_col2 = st.columns(
        2,
        gap="large"
    )

    # ========================================================
    # LEFT PROFILE CARD
    # ========================================================

    with profile_col1:

        with st.container(
            border=True
        ):

            st.caption(
                t("name")
            )

            st.write(
                f"**{profile['name']}**"
            )

            st.caption(
                t("age")
            )

            st.write(
                f"**{profile['age']}**"
            )

            st.caption(
                t("state")
            )

            st.write(
                f"**{opt(profile['state'])}**"
            )

            st.caption(
                t("district")
            )

            st.write(
                f"**{profile['district']}**"
            )

            st.caption(
                t("category")
            )

            st.write(
                f"**{opt(profile['target_category'])}**"
            )

    # ========================================================
    # RIGHT PROFILE CARD
    # ========================================================

    with profile_col2:

        with st.container(
            border=True
        ):

            st.caption(
                t("business_type")
            )

            st.write(
                f"**{opt(profile['business_type'])}**"
            )

            st.caption(
                t("business_stage")
            )

            st.write(
                f"**{opt(profile['business_stage'])}**"
            )

            st.caption(
                t("annual_income")
            )

            st.write(
                f"**₹{profile['annual_income']:,.0f}**"
            )

            st.caption(
                t("investment")
            )

            st.write(
                f"**₹{profile['investment_required']:,.0f}**"
            )

            st.caption(
                t("employees")
            )

            st.write(
                f"**{profile['employees']}**"
            )

    # ========================================================
    # RECOMMENDED SCHEMES
    # ========================================================

    st.divider()

    st.markdown(
        f"""
        <div class="section-title">
            {t("recommended_schemes")}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write(
        f"**{len(results)}** {t('found_schemes')}"
    )

    # ========================================================
    # NO RESULTS
    # ========================================================

    if not results:

        st.warning(
            "No potential schemes found for this profile."
        )

    # ========================================================
    # SCHEME CARDS
    # ========================================================

    for index, result in enumerate(results):

        score = result["score"]

        if score >= 80:
            status = t("strong_match")

        elif score >= 60:
            status = t("moderate_match")

        else:
            status = t("low_match")

        with st.container(
            border=True
        ):

            if index == 0:

                st.markdown(
                    f"""
                    <div class="top-match">
                        {t("top_match")}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.markdown(
                f"""
                <div class="scheme-title">
                    #{index + 1}
                    {scheme_text(result["scheme_name"])}
                </div>
                """,
                unsafe_allow_html=True
            )

            col1, col2 = st.columns(
                [1, 3],
                gap="large"
            )

            # ------------------------------------------------
            # SCORE
            # ------------------------------------------------

            with col1:

                st.metric(
                    t("match_score"),
                    f"{score}%"
                )

                st.progress(
                    score / 100
                )

                st.write(
                    status
                )

            # ------------------------------------------------
            # BENEFIT
            # ------------------------------------------------

            with col2:

                st.caption(
                    t("benefit")
                )

                st.write(
                    f"**{scheme_text(result['benefit_type'])}**"
                )

                st.write(
                    scheme_text(
                        result["benefit_description"]
                    )
                )

            # ------------------------------------------------
            # WHY MATCHES
            # ------------------------------------------------

            with st.expander(
                t("why_matches")
            ):

                for reason in result["reasons"]:

                    st.write(
                        f"✅ {scheme_text(reason)}"
                    )

                if result["warnings"]:

                    st.write(
                        f"### {t('things_to_verify')}"
                    )

                    for warning in result["warnings"]:

                        st.write(
                            f"⚠️ {scheme_text(warning)}"
                        )

            # ------------------------------------------------
            # OFFICIAL INFORMATION
            # ------------------------------------------------

            st.link_button(
                f"🔗 {t('official_info')}",
                result["official_url"]
            )


    # ========================================================
    # DOCUMENT READINESS
    # ========================================================
    
    st.divider()
    
    with st.container(border=True):
    
        st.markdown("### 📄 Document Readiness")
    
        st.write(
            "Upload and manage the documents required "
            "for your recommended government schemes."
        )
    
        if st.button(
            "Open Document Readiness",
            use_container_width=True,
            key="open_document_readiness"
        ):
    
            st.session_state["selected_profile_id"] = (
                profile["id"]
            )
    
            st.switch_page(
                "pages/6_Document_Readiness.py"
            )

            
    # ========================================================
    # AI ASSISTANT
    # ========================================================

    st.info(
        t("ai_note")
    )

    # ========================================================
    # DISCLAIMER
    # ========================================================

    st.markdown(
        f"""
        <div class="disclaimer">
            {t("disclaimer")}
        </div>
        """,
        unsafe_allow_html=True
    )

    