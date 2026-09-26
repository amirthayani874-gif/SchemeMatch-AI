import streamlit as st

from modules.database import (
    get_profiles,
    delete_profile
)

from modules.translations import (
    render_language_selector,
    t,
    opt
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Profiles | SchemeMatch AI",
    page_icon="👤",
    layout="wide"
)


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
    max-width: 1150px;
}

.page-header {
    padding: 2rem;
    border-radius: 18px;
    background: linear-gradient(135deg, #f5f7ff, #eef4ff);
    border: 1px solid #e2e7f5;
    margin-bottom: 2rem;
}

.page-title {
    font-size: 2.3rem;
    font-weight: 700;
    color: #202638;
    margin-bottom: 0.3rem;
}

.page-description {
    color: #606b80;
    font-size: 1rem;
}

.profile-card {
    padding: 1.4rem;
    border: 1px solid #e3e6ed;
    border-radius: 16px;
    background: #ffffff;
    margin-bottom: 1rem;
}

.profile-name {
    font-size: 1.35rem;
    font-weight: 700;
    color: #202638;
    margin-bottom: 0.8rem;
}

.profile-label {
    font-size: 0.78rem;
    color: #737d91;
    margin-top: 0.4rem;
}

.profile-value {
    font-size: 0.95rem;
    font-weight: 600;
    color: #202638;
}

.empty-box {
    padding: 2.5rem;
    text-align: center;
    border: 1px dashed #cfd5e2;
    border-radius: 16px;
    background: #fafbfe;
}

.stButton > button {
    border-radius: 10px;
    height: 2.8rem;
    font-weight: 600;
}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# PAGE HEADER
# ============================================================

st.markdown(
    """
<div class="page-header">

<div class="page-title">
👤 Stored Profiles
</div>

<div class="page-description">
Manage your saved entrepreneur profiles and find schemes for each profile.
</div>

</div>
""",
    unsafe_allow_html=True
)


# ============================================================
# CREATE NEW PROFILE
# ============================================================

if st.button(
    "➕ Create New Profile",
    use_container_width=True
):

    # Make sure no previously selected profile
    # is accidentally reused.
    st.session_state.pop("selected_profile_id", None)
    st.session_state.pop("profile", None)
    st.session_state.pop("profile_id", None)

    # Clear old matching results
    st.session_state.pop("results", None)
    st.session_state.pop("all_results", None)

    st.switch_page("pages/1_Find_Schemes.py")


st.write("")


# ============================================================
# LOAD STORED PROFILES
# ============================================================

profiles = get_profiles()


# ============================================================
# EMPTY STATE
# ============================================================

if not profiles:

    st.markdown(
        """
<div class="empty-box">

<h3>📂 No Stored Profiles</h3>

<p>
You don't have any saved entrepreneur profiles yet.
</p>

</div>
""",
        unsafe_allow_html=True
    )

    st.stop()


# ============================================================
# PROFILE COUNT
# ============================================================

st.markdown(
    f"### Your Profiles ({len(profiles)})"
)

st.write("")


# ============================================================
# DISPLAY PROFILES
# ============================================================

for profile in profiles:

    # --------------------------------------------------------
    # Support dictionary / sqlite Row style results
    # --------------------------------------------------------

    try:
        profile_id = profile["id"]
        name = profile["name"]
        age = profile["age"]
        state = profile["state"]
        district = profile["district"]
        category = profile["category"]
        business_type = profile["business_type"]
        business_stage = profile["business_stage"]
        annual_income = profile["annual_income"]
        investment = profile["investment"]
        employees = profile["employees"]

    except (TypeError, KeyError):

        # Fallback for tuple-style database results
        profile_id = profile[0]
        name = profile[1]
        age = profile[2]
        state = profile[3]
        district = profile[4]
        category = profile[5]
        business_type = profile[6]
        business_stage = profile[7]
        annual_income = profile[8]
        investment = profile[9]
        employees = profile[10]


    # ========================================================
    # PROFILE CARD
    # ========================================================

    with st.container(border=True):

        st.markdown(
            f"""
<div class="profile-name">
👤 {name}
</div>
""",
            unsafe_allow_html=True
        )

        col1, col2, col3 = st.columns(3)

        # ----------------------------------------------------
        # COLUMN 1
        # ----------------------------------------------------

        with col1:

            st.markdown(
                f"""
<div class="profile-label">Age</div>
<div class="profile-value">{age}</div>

<div class="profile-label">Location</div>
<div class="profile-value">{district}, {opt(state)}</div>

<div class="profile-label">Category</div>
<div class="profile-value">{opt(category)}</div>
""",
                unsafe_allow_html=True
            )


        # ----------------------------------------------------
        # COLUMN 2
        # ----------------------------------------------------

        with col2:

            st.markdown(
                f"""
<div class="profile-label">Business Type</div>
<div class="profile-value">{opt(business_type)}</div>

<div class="profile-label">Business Stage</div>
<div class="profile-value">{opt(business_stage)}</div>

<div class="profile-label">Employees</div>
<div class="profile-value">{employees}</div>
""",
                unsafe_allow_html=True
            )


        # ----------------------------------------------------
        # COLUMN 3
        # ----------------------------------------------------

        with col3:

            st.markdown(
                f"""
<div class="profile-label">Annual Income</div>
<div class="profile-value">₹{annual_income:,.0f}</div>

<div class="profile-label">Investment Required</div>
<div class="profile-value">₹{investment:,.0f}</div>

<div class="profile-label">Profile ID</div>
<div class="profile-value">PROF-{profile_id:03d}</div>
""",
                unsafe_allow_html=True
            )


        st.write("")


        # ====================================================
        # ACTION BUTTONS
        # ====================================================

        action_col1, action_col2 = st.columns([3, 1])


        # ----------------------------------------------------
        # USE PROFILE
        # ----------------------------------------------------

        with action_col1:

            if st.button(
                "🎯 Use This Profile",
                key=f"use_profile_{profile_id}",
                use_container_width=True
            ):

                # Store ONLY the selected profile ID.
                #
                # Find My Schemes will load the complete
                # profile from the database.
                st.session_state["selected_profile_id"] = profile_id

                # Remove old results so the selected profile
                # starts with a clean scheme-matching state.
                st.session_state.pop("results", None)
                st.session_state.pop("all_results", None)

                st.switch_page(
                    "pages/1_Find_Schemes.py"
                )


        # ----------------------------------------------------
        # DELETE PROFILE
        # ----------------------------------------------------

        with action_col2:

            if st.button(
                "🗑️ Delete",
                key=f"delete_profile_{profile_id}",
                use_container_width=True
            ):

                st.session_state[
                    f"confirm_delete_{profile_id}"
                ] = True


        # ====================================================
        # DELETE CONFIRMATION
        # ====================================================

        if st.session_state.get(
            f"confirm_delete_{profile_id}",
            False
        ):

            st.warning(
                f"Delete profile **{name}**? "
                "This will also remove its stored profile-related data."
            )

            confirm_col1, confirm_col2 = st.columns(2)


            with confirm_col1:

                if st.button(
                    "Yes, Delete",
                    key=f"confirm_yes_{profile_id}",
                    use_container_width=True
                ):

                    delete_profile(profile_id)

                    st.session_state.pop(
                        f"confirm_delete_{profile_id}",
                        None
                    )

                    # If the deleted profile was selected,
                    # clear the active profile.
                    if st.session_state.get(
                        "selected_profile_id"
                    ) == profile_id:

                        st.session_state.pop(
                            "selected_profile_id",
                            None
                        )

                        st.session_state.pop(
                            "profile",
                            None
                        )

                        st.session_state.pop(
                            "profile_id",
                            None
                        )

                    st.success(
                        f"Profile **{name}** deleted."
                    )

                    st.rerun()


            with confirm_col2:

                if st.button(
                    "Cancel",
                    key=f"cancel_delete_{profile_id}",
                    use_container_width=True
                ):

                    st.session_state.pop(
                        f"confirm_delete_{profile_id}",
                        None
                    )

                    st.rerun()