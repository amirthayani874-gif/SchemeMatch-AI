import streamlit as st
import pandas as pd
from pathlib import Path

from modules.database import (
    initialize_database,
    initialize_document_upload_table,
    get_profiles,
    get_scheme_documents,
    get_document_upload,
    save_document_upload,
    delete_document_upload,
)


# ========================================================
# PAGE CONFIGURATION
# ========================================================

st.set_page_config(
    page_title="Document Readiness | SchemeMatch AI",
    page_icon="📄",
    layout="wide"
)


# ========================================================
# INITIALIZE DATABASE
# ========================================================

initialize_database()
initialize_document_upload_table()


# ========================================================
# PATHS
# ========================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ========================================================
# LOAD SCHEMES
# ========================================================

schemes = pd.read_csv(
    BASE_DIR / "data" / "schemes.csv"
)


# ========================================================
# PAGE CSS
# ========================================================

st.markdown(
    """
    <style>

    .block-container {
        max-width: 1200px;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    /* Make expanders compact */

    div[data-testid="stExpander"] {
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        margin-bottom: 0.7rem;
    }

    div[data-testid="stExpander"] details summary {
        padding: 0.8rem 1rem;
    }

    /* Smaller file uploader */

    div[data-testid="stFileUploader"] {
        margin-top: 0;
    }

    /* Profile information */

    .profile-box {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 0.8rem 1rem;
        margin: 1rem 0 1.2rem 0;
    }

    .profile-name {
        font-size: 1.05rem;
        font-weight: 700;
        color: #172554;
    }

    .profile-info {
        font-size: 0.85rem;
        color: #64748b;
        margin-top: 0.2rem;
    }

    .document-name {
        font-weight: 600;
        font-size: 0.9rem;
    }

    .document-file {
        font-size: 0.78rem;
        color: #64748b;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ========================================================
# HEADER
# ========================================================

st.title("📄 Document Readiness")

st.caption(
    "Upload and manage the documents required for your "
    "recommended government schemes."
)


# ========================================================
# LOAD PROFILES
# ========================================================

profiles = get_profiles()


if not profiles:

    st.info(
        "No stored profiles found. Please create a profile first."
    )

    st.stop()


# ========================================================
# FIND ACTIVE PROFILE
# ========================================================

profile_id = st.session_state.get("profile_id")

if profile_id is None:
    profile_id = st.session_state.get("selected_profile_id")


# Try profile object as fallback
if profile_id is None:

    active_profile = st.session_state.get("profile")

    if isinstance(active_profile, dict):
        profile_id = active_profile.get("id")


if profile_id is None:

    st.warning(
        "Please select a stored profile before opening "
        "Document Readiness."
    )

    st.stop()


# ========================================================
# FIND PROFILE
# ========================================================

selected_profile = None

for profile in profiles:

    if int(profile[0]) == int(profile_id):

        selected_profile = profile
        break


if selected_profile is None:

    st.error(
        "The selected profile could not be found."
    )

    st.stop()


# ========================================================
# PROFILE INFORMATION
# ========================================================

# IMPORTANT:
# No HTML is used here.
# This prevents <div> code from appearing on the page.

st.markdown(
    f"""
    **👤 {selected_profile[1]}**

    `PROF-{selected_profile[0]:03d}` • 📍 {selected_profile[3]}, {selected_profile[4]}
    """
)

st.divider()


# ========================================================
# GET RECOMMENDED SCHEMES
# ========================================================

recommended_schemes = st.session_state.get(
    "results",
    []
)


if not recommended_schemes:

    st.info(
        "No recommended schemes are available for this profile yet."
    )

    st.stop()


# ========================================================
# SCHEME ID RESOLVER
# ========================================================

def resolve_scheme_id(result):

    # First try the scheme_id from matching results
    result_id = result.get("scheme_id")

    if result_id:

        result_id = str(result_id).strip()

        documents = get_scheme_documents(
            result_id
        )

        if documents:
            return result_id


    # Try normalized ID
    if result_id:

        normalized_id = (
            str(result_id)
            .replace(" ", "")
            .replace("-", "")
            .upper()
        )

        known_ids = {
            "PMMY": "PMMY",
            "PMEGP": "PMEGP",
            "CGTMSE": "CGTMSE",
            "PMVISHWAKARMA": "PMVISHWAKARMA",
        }

        if normalized_id in known_ids:

            scheme_id = known_ids[normalized_id]

            if get_scheme_documents(scheme_id):

                return scheme_id


    # Fall back to scheme name
    scheme_name = str(
        result.get(
            "scheme_name",
            ""
        )
    ).lower()


    if "mudra" in scheme_name:

        return "PMMY"


    if "employment generation" in scheme_name:

        return "PMEGP"


    if "credit guarantee" in scheme_name:

        return "CGTMSE"


    if "vishwakarma" in scheme_name:

        return "PMVISHWAKARMA"


    return result_id


# ========================================================
# SECTION TITLE
# ========================================================

st.subheader("🏛️ Recommended Schemes")

st.caption(
    "Select a scheme below to view its required documents."
)


# ========================================================
# DISPLAY SCHEMES
# ========================================================

for scheme_index, result in enumerate(
    recommended_schemes
):

    scheme_name = result.get(
        "scheme_name",
        "Government Scheme"
    )

    score = result.get(
        "score",
        0
    )

    scheme_id = resolve_scheme_id(
        result
    )


    # ----------------------------------------------------
    # GET DOCUMENTS
    # ----------------------------------------------------

    required_documents = get_scheme_documents(
        scheme_id
    )


    # ----------------------------------------------------
    # SCHEME EXPANDER
    # ----------------------------------------------------

    with st.expander(
        f"{scheme_index + 1}. {scheme_name}   •   Match Score: {score}%",
        expanded=False
    ):

        # =================================================
        # NO DOCUMENT CONFIGURATION
        # =================================================

        if not required_documents:

            st.warning(
                "📄 No document requirements are configured "
                "for this scheme yet."
            )

            continue


        # =================================================
        # CHECK CURRENT UPLOADS
        # =================================================

        uploaded_count = 0

        document_records = []


        for document_name in required_documents:

            existing_upload = get_document_upload(
                int(profile_id),
                scheme_id,
                document_name
            )

            is_available = (
                existing_upload is not None
            )

            if is_available:
                uploaded_count += 1

            document_records.append(
                (
                    document_name,
                    existing_upload,
                    is_available
                )
            )


        # =================================================
        # READINESS SUMMARY
        # =================================================

        total_documents = len(
            required_documents
        )

        readiness = round(
            (
                uploaded_count /
                total_documents
            ) * 100
        )


        st.progress(
            readiness / 100
        )

        st.caption(
            f"📊 **Document Readiness: {readiness}%** "
            f"— {uploaded_count} of {total_documents} "
            f"documents uploaded"
        )


        st.divider()


        # =================================================
        # DOCUMENTS
        # =================================================

        for document_index, (
            document_name,
            existing_upload,
            is_available
        ) in enumerate(
            document_records
        ):

            # --------------------------------------------
            # COMPACT ROW
            # --------------------------------------------

            col1, col2, col3 = st.columns(
                [4.5, 1.5, 2.2],
                vertical_alignment="center"
            )


            # --------------------------------------------
            # DOCUMENT NAME
            # --------------------------------------------

            with col1:

                st.markdown(
                    f"**📄 {document_name}**"
                )

                if is_available:

                    st.caption(
                        f"Uploaded: {existing_upload[4]}"
                    )

                else:

                    st.caption(
                        "No document uploaded"
                    )


            # --------------------------------------------
            # STATUS
            # --------------------------------------------

            with col2:

                if is_available:

                    st.success(
                        "✓ Available",
                        icon="📄"
                    )

                else:

                    st.error(
                        "✕ Missing",
                        icon="📄"
                    )


            # --------------------------------------------
            # UPLOAD / REMOVE
            # --------------------------------------------

            with col3:

                if not is_available:

                    uploader_key = (
                        f"document_"
                        f"{profile_id}_"
                        f"{scheme_id}_"
                        f"{document_index}"
                    )

                    uploaded_file = st.file_uploader(
                        "Upload",
                        type=[
                            "pdf",
                            "jpg",
                            "jpeg",
                            "png",
                            "doc",
                            "docx"
                        ],
                        key=uploader_key,
                        label_visibility="collapsed"
                    )


                    if uploaded_file is not None:

                        try:

                            save_document_upload(
                                int(profile_id),
                                scheme_id,
                                document_name,
                                uploaded_file
                            )

                            st.success(
                                "Uploaded successfully",
                                icon="✅"
                            )

                            st.rerun()

                        except Exception as error:

                            st.error(
                                f"Upload failed: {error}"
                            )


                else:

                    remove_key = (
                        f"remove_"
                        f"{profile_id}_"
                        f"{scheme_id}_"
                        f"{document_index}"
                    )


                    if st.button(
                        "Remove",
                        key=remove_key,
                        use_container_width=True
                    ):

                        try:

                            delete_document_upload(
                                int(profile_id),
                                scheme_id,
                                document_name
                            )

                            st.rerun()

                        except Exception as error:

                            st.error(
                                f"Could not remove document: {error}"
                            )


            st.divider()


# ========================================================
# FOOTER
# ========================================================

st.caption(
    "Uploaded documents are stored locally for the selected "
    "profile and scheme. Final document requirements should "
    "always be verified on the official government portal."
)
