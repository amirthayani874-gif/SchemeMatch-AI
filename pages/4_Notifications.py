import streamlit as st
import pandas as pd
from pathlib import Path


from modules.database import (
    get_profiles,
    get_notifications,
    mark_notification_read,
    get_notification_status,
    set_notification_status,
    delete_profile
)


from modules.notifications import (
    run_notification_check
)


from modules.translations import (
    render_language_selector,
    t,
    scheme_text
)


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Notifications | SchemeMatch AI",
    page_icon="🔔",
    layout="wide"
)


# --------------------------------------------------
# CENTER PAGE CONTENT
# --------------------------------------------------

st.markdown(
    """
    <style>

    /* Main Streamlit content container */
    [data-testid="stMainBlockContainer"] {
        max-width: 1080px;
        margin-left: auto;
        margin-right: auto;
        padding-left: 0rem;
        padding-right: 0rem;
    }

    /* Compatibility with older Streamlit versions */
    .block-container {
        max-width: 1080px;
        margin-left: auto;
        margin-right: auto;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# LANGUAGE
# --------------------------------------------------

render_language_selector()


# --------------------------------------------------
# LOAD SCHEMES
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

try:

    schemes = pd.read_csv(
        BASE_DIR / "data" / "schemes.csv"
    )

except Exception:

    schemes = pd.DataFrame()


# --------------------------------------------------
# REAL-TIME NOTIFICATION CHECK
# --------------------------------------------------

@st.fragment(run_every="60s")
def realtime_notification_check():

    if not schemes.empty:

        run_notification_check(
            schemes
        )


realtime_notification_check()


# --------------------------------------------------
# PAGE TITLE
# --------------------------------------------------

st.markdown(
    f"""
    <h1 style="margin-bottom: 5px;">
        🔔 {t("notifications")}
    </h1>

    <p style="
        color: #777;
        font-size: 17px;
    ">
        {t("notifications_description")}
    </p>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# GET PROFILES
# --------------------------------------------------

profiles = get_profiles()


if not profiles:

    st.info(
        f"👤 {t('no_profiles')}"
    )

    st.stop()


# --------------------------------------------------
# PROFILE SELECTION
# --------------------------------------------------

profile_options = {}


for profile in profiles:

    profile_id = profile[0]
    profile_name = profile[1]

    profile_options[
        f"{profile_name} (ID: {profile_id})"
    ] = profile_id


selected_profile_name = st.selectbox(
    f"👤 {t('select_profile')}",
    list(profile_options.keys())
)


selected_profile_id = profile_options[
    selected_profile_name
]


# --------------------------------------------------
# NOTIFICATION STATUS
# --------------------------------------------------

notifications_enabled = get_notification_status(
    selected_profile_id
)


# --------------------------------------------------
# PROFILE ACTIONS
# --------------------------------------------------

st.markdown(
    f"### {t('profile_settings')}"
)


col1, col2 = st.columns(2)


# --------------------------------------------------
# NOTIFICATION SETTINGS
# --------------------------------------------------

with col1:

    if notifications_enabled:

        st.success(
            f"🔔 {t('notifications_enabled')}"
        )

        if st.button(
            f"🔕 {t('disable_notifications')}",
            key=f"disable_notifications_{selected_profile_id}",
            use_container_width=True
        ):

            set_notification_status(
                selected_profile_id,
                False
            )

            st.rerun()

    else:

        st.warning(
            f"🔕 {t('notifications_disabled')}"
        )

        if st.button(
            f"🔔 {t('enable_notifications')}",
            key=f"enable_notifications_{selected_profile_id}",
            use_container_width=True
        ):

            set_notification_status(
                selected_profile_id,
                True
            )

            st.rerun()


# --------------------------------------------------
# DELETE PROFILE
# --------------------------------------------------

with col2:

    st.error(
        f"🗑️ {t('delete_profile')}"
    )

    if st.button(
        f"🗑️ {t('delete_profile')}",
        key=f"delete_profile_{selected_profile_id}",
        use_container_width=True
    ):

        st.session_state[
            f"confirm_delete_{selected_profile_id}"
        ] = True


# --------------------------------------------------
# DELETE CONFIRMATION DIALOG
# --------------------------------------------------

@st.dialog(
    t("confirm_profile_deletion")
)
def confirm_delete_dialog():

    st.markdown(
        f"### {t('delete_profile')} **{selected_profile_name}**?"
    )

    st.write(
        t("delete_profile_question")
    )

    st.warning(
        t("delete_profile_warning")
    )

    st.write("")

    col1, col2 = st.columns(2)


    # --------------------------------------------------
    # CANCEL
    # --------------------------------------------------

    with col1:

        if st.button(
            f"❌ {t('cancel')}",
            use_container_width=True
        ):

            st.session_state[
                f"confirm_delete_{selected_profile_id}"
            ] = False

            st.rerun()


    # --------------------------------------------------
    # CONFIRM DELETE
    # --------------------------------------------------

    with col2:

        if st.button(
            f"🗑️ {t('yes_delete')}",
            use_container_width=True
        ):

            delete_profile(
                selected_profile_id
            )

            # Clear stored matching results
            st.session_state.pop(
                "results",
                None
            )

            st.session_state.pop(
                "all_results",
                None
            )

            st.session_state[
                f"confirm_delete_{selected_profile_id}"
            ] = False

            st.rerun()


# --------------------------------------------------
# OPEN DELETE DIALOG
# --------------------------------------------------

if st.session_state.get(
    f"confirm_delete_{selected_profile_id}",
    False
):

    confirm_delete_dialog()


# --------------------------------------------------
# DIVIDER
# --------------------------------------------------

st.divider()


# --------------------------------------------------
# GET NOTIFICATIONS
# --------------------------------------------------

notifications = get_notifications(
    selected_profile_id
)


# --------------------------------------------------
# NOTIFICATION COUNT
# --------------------------------------------------

unread_count = sum(
    1
    for notification in notifications
    if notification[6] == 0
)


col1, col2 = st.columns(2)


with col1:

    st.metric(
        f"🔔 {t('total_notifications')}",
        len(notifications)
    )


with col2:

    st.metric(
        f"📩 {t('unread_notifications')}",
        unread_count
    )


st.divider()


# --------------------------------------------------
# NO NOTIFICATIONS
# --------------------------------------------------

if not notifications:

    st.success(
        f"✅ {t('no_notifications')}"
    )

    st.stop()


# --------------------------------------------------
# NOTIFICATION CARDS
# --------------------------------------------------

for notification in notifications:

    notification_id = notification[0]
    profile_id = notification[1]
    scheme_id = notification[2]
    notification_type = notification[3]
    title = notification[4]
    message = notification[5]
    is_read = notification[6]
    created_at = notification[7]


    # --------------------------------------------------
    # FIND SCHEME INFORMATION
    # --------------------------------------------------

    scheme_name = scheme_id
    scheme_url = None


    if not schemes.empty and scheme_id:

        matching_scheme = schemes[
            schemes["scheme_id"] == scheme_id
        ]


        if not matching_scheme.empty:

            scheme_name = matching_scheme.iloc[0][
                "scheme_name"
            ]

            scheme_url = matching_scheme.iloc[0][
                "official_url"
            ]


    # --------------------------------------------------
    # NOTIFICATION TYPE
    # --------------------------------------------------

    if notification_type == "NEW_SCHEME":

        icon = "🆕"

        translated_title = t(
            "new_scheme_available"
        )

        translated_message = (
            f"{scheme_text(scheme_name)} "
            f"{t('may_be_relevant')}"
        )


    elif notification_type == "SCHEME_UPDATED":

        icon = "🔄"

        translated_title = t(
            "scheme_updated"
        )

        translated_message = (
            f"{t('important_information_changed')} "
            f"{scheme_text(scheme_name)}."
        )


    elif notification_type == "DEADLINE":

        icon = "⏰"

        translated_title = title

        translated_message = message


    else:

        icon = "🔔"

        translated_title = title

        translated_message = message


    # --------------------------------------------------
    # UNREAD NOTIFICATION
    # --------------------------------------------------

    if is_read == 0:

        with st.container(
            border=True
        ):

            st.markdown(
                f"### {icon} {translated_title}"
            )


            st.markdown(
                f"**{scheme_text(scheme_name)}**"
            )


            st.write(
                translated_message
            )


            st.caption(
                f"🕒 {created_at}  •  🔵 New"
            )


            col1, col2 = st.columns(2)


            with col1:

                if st.button(
                    f"✓ {t('mark_as_read')}",
                    key=f"read_{notification_id}",
                    use_container_width=True
                ):

                    mark_notification_read(
                        notification_id
                    )

                    st.rerun()


            with col2:

                if scheme_url:

                    st.link_button(
                        f"🔗 {t('official_info')}",
                        scheme_url,
                        use_container_width=True
                    )


    # --------------------------------------------------
    # READ NOTIFICATION
    # --------------------------------------------------

    else:

        with st.container(
            border=True
        ):

            st.markdown(
                f"### {icon} {translated_title}"
            )


            st.markdown(
                f"**{scheme_text(scheme_name)}**"
            )


            st.write(
                translated_message
            )


            st.caption(
                f"🕒 {created_at}  •  ✓ Read"
            )


            if scheme_url:

                st.link_button(
                    f"🔗 {t('official_info')}",
                    scheme_url,
                    use_container_width=True
                )


    st.write("")