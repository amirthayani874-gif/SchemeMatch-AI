import streamlit as st
from groq import Groq

from modules.ai_assistant import ask_ai
from modules.translations import (
    render_language_selector,
    t,
    opt
)

from modules.database import (
    get_profile
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Assistant | SchemeMatch AI",
    page_icon="🤖",
    layout="wide"
)


# ============================================================
# LANGUAGE
# ============================================================

render_language_selector()

language = st.session_state.get(
    "language",
    "English"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        max-width: 1500px;
        padding-top: 2rem;
        padding-bottom: 3rem;
        padding-left: 3rem;
        padding-right: 3rem;
    }

    .page-header {
        padding: 1.6rem 2rem;
        border-radius: 16px;
        background: linear-gradient(
            135deg,
            #f5f7ff,
            #eef4ff
        );
        border: 1px solid #e1e6f2;
        margin-bottom: 1.8rem;
    }

    .page-title {
        font-size: 2.3rem;
        font-weight: 700;
        color: #202638;
        margin-bottom: 0.3rem;
    }

    .page-description {
        font-size: 1rem;
        color: #5d687d;
        line-height: 1.6;
    }

    .section-title {
        font-size: 1.35rem;
        font-weight: 650;
        color: #202638;
        margin-bottom: 0.8rem;
    }

    .profile-summary {
        padding: 1.2rem 1.4rem;
        border: 1px solid #e1e5ec;
        border-radius: 12px;
        background: #fafbfc;
        margin-bottom: 1rem;
    }

    .profile-label {
        color: #737d8e;
        font-size: 0.82rem;
        margin-bottom: 0.15rem;
    }

    .profile-value {
        color: #202638;
        font-weight: 600;
        margin-bottom: 0.7rem;
    }

    .stButton > button {
        border-radius: 9px;
        min-height: 2.7rem;
        font-weight: 600;
    }

    [data-testid="stChatInput"] {
        margin-top: 1rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.title("🤖 AI Assistant")

st.write(
    "Ask questions about your recommended government "
    "schemes and get simple, personalized guidance."
)


# ============================================================
# PROFILE NORMALIZATION
# ============================================================

def normalize_profile(raw_profile):
    """
    Convert different profile formats used by SchemeMatch AI
    into one consistent dictionary format.

    Supported formats:
        1. Dictionary profile
        2. SQLite profile tuple
        3. Profile ID
        4. None
    """

    # --------------------------------------------------------
    # No profile
    # --------------------------------------------------------

    if raw_profile is None:
        return None

    # --------------------------------------------------------
    # Dictionary profile
    # --------------------------------------------------------

    if isinstance(raw_profile, dict):

        profile = dict(raw_profile)

        # ----------------------------------------------------
        # Handle alternate key names
        # ----------------------------------------------------

        if "target_category" not in profile:

            profile["target_category"] = profile.get(
                "category",
                ""
            )

        if "investment_required" not in profile:

            profile["investment_required"] = profile.get(
                "investment",
                0
            )

        if "district" not in profile:

            profile["district"] = ""

        if "state" not in profile:

            profile["state"] = ""

        if "business_type" not in profile:

            profile["business_type"] = ""

        if "business_stage" not in profile:

            profile["business_stage"] = ""

        if "name" not in profile:

            profile["name"] = "User"

        if "age" not in profile:

            profile["age"] = 0

        return profile

    # --------------------------------------------------------
    # SQLite profile ID
    # --------------------------------------------------------

    if isinstance(raw_profile, int):

        database_profile = get_profile(
            raw_profile
        )

        if database_profile is None:
            return None

        raw_profile = database_profile

    # --------------------------------------------------------
    # SQLite tuple
    #
    # Database structure:
    #
    # 0  id
    # 1  name
    # 2  age
    # 3  state
    # 4  district
    # 5  category
    # 6  business_type
    # 7  business_stage
    # 8  annual_income
    # 9  investment
    # 10 employees
    # --------------------------------------------------------

    if isinstance(
        raw_profile,
        (tuple, list)
    ):

        if len(raw_profile) < 10:
            return None

        return {
            "id": raw_profile[0],
            "name": raw_profile[1],
            "age": raw_profile[2],
            "state": raw_profile[3],
            "district": raw_profile[4],
            "target_category": raw_profile[5],
            "category": raw_profile[5],
            "business_type": raw_profile[6],
            "business_stage": raw_profile[7],
            "annual_income": raw_profile[8],
            "investment_required": raw_profile[9],
            "investment": raw_profile[9],
            "employees": raw_profile[10]
            if len(raw_profile) > 10
            else 0
        }

    return None


# ============================================================
# FIND ACTIVE PROFILE
# ============================================================

raw_profile = st.session_state.get(
    "profile"
)


# ------------------------------------------------------------
# If profile object is missing, try selected profile ID
# ------------------------------------------------------------

if raw_profile is None:

    profile_id = st.session_state.get(
        "profile_id"
    )

    if profile_id is None:

        profile_id = st.session_state.get(
            "selected_profile_id"
        )

    if profile_id is not None:

        raw_profile = profile_id


# ------------------------------------------------------------
# Normalize profile
# ------------------------------------------------------------

profile = normalize_profile(
    raw_profile
)


# ============================================================
# PROFILE REQUIRED
# ============================================================

if profile is None:

    st.warning(
        f"⚠️ {t('profile_required')}"
    )

    st.info(
        "Please select or create a profile before using "
        "the AI Assistant."
    )

    if st.button(
        f"🎯 {t('go_to_find_schemes')}",
        use_container_width=True
    ):

        st.switch_page(
            "pages/1_Find_Schemes.py"
        )

    st.stop()


# ============================================================
# STORE NORMALIZED PROFILE
# ============================================================

st.session_state["profile"] = profile

if profile.get("id") is not None:

    st.session_state["profile_id"] = (
        profile["id"]
    )


# ============================================================
# LOAD SCHEME RESULTS
# ============================================================

results = st.session_state.get(
    "results",
    []
)

all_results = st.session_state.get(
    "all_results",
    results
)


# Make sure results are always lists

if results is None:
    results = []

if all_results is None:
    all_results = []


# ============================================================
# INITIALIZE CHAT HISTORY
# ============================================================

if (
    "chat_history"
    not in st.session_state
):

    st.session_state["chat_history"] = []


# ============================================================
# PROFILE SUMMARY
# ============================================================

with st.expander("👤 Your Profile", expanded=False):

    profile_col1, profile_col2 = st.columns(2)

    with profile_col1:

        st.markdown("**Full Name**")
        st.write(profile.get("name", "Not available"))

        st.markdown("**Age**")
        st.write(profile.get("age", "Not available"))

        st.markdown("**State**")
        st.write(opt(profile.get("state", "Not available")))

        st.markdown("**District**")
        st.write(
            opt(
                profile.get(
                    "district",
                    "Not available"
                )
            )
        )

        st.markdown("**Entrepreneur Category**")
        st.write(
            opt(
                profile.get(
                    "target_category",
                    profile.get(
                        "category",
                        "Not available"
                    )
                )
            )
        )

    with profile_col2:

        st.markdown("**Business Type**")
        st.write(
            opt(
                profile.get(
                    "business_type",
                    "Not available"
                )
            )
        )

        st.markdown("**Business Stage**")
        st.write(
            opt(
                profile.get(
                    "business_stage",
                    "Not available"
                )
            )
        )

        st.markdown("**Investment Required**")

        investment = profile.get(
            "investment_required",
            profile.get(
                "investment",
                0
            )
        )

        try:
            st.write(f"₹{float(investment):,.0f}")
        except (ValueError, TypeError):
            st.write("Not available")

    

# ============================================================
# SUGGESTED QUESTIONS
# ============================================================

st.markdown(
    f"""
    <div class="section-title">
        💡 {t("try_asking")}
    </div>
    """,
    unsafe_allow_html=True
)


suggested_questions = {

    "English": [
        "Why was my top scheme recommended?",
        "Which scheme is suitable for my investment?",
        "What should I verify before applying?",
        "Can you explain my top matched scheme?",
        "What documents might I need?"
    ],

    "தமிழ்": [
        "எனக்கு இந்த சிறந்த திட்டம் ஏன் பரிந்துரைக்கப்பட்டது?",
        "எனது முதலீட்டிற்கு எந்த திட்டம் பொருத்தமானது?",
        "விண்ணப்பிப்பதற்கு முன் நான் எதை சரிபார்க்க வேண்டும்?",
        "எனக்கு பொருந்திய சிறந்த திட்டத்தை விளக்க முடியுமா?",
        "என்ன ஆவணங்கள் தேவைப்படலாம்?"
    ],

    "हिन्दी": [
        "मेरे लिए यह योजना क्यों सुझाई गई?",
        "मेरे निवेश के लिए कौन सी योजना उपयुक्त है?",
        "आवेदन करने से पहले मुझे क्या सत्यापित करना चाहिए?",
        "मेरी सबसे अच्छी योजना को समझा सकते हैं?",
        "मुझे किन दस्तावेज़ों की आवश्यकता हो सकती है?"
    ],

    "മലയാളം": [
        "എനിക്ക് ഈ പദ്ധതി എന്തുകൊണ്ടാണ് ശുപാർശ ചെയ്തത്?",
        "എന്റെ നിക്ഷേപത്തിന് ഏത് പദ്ധതി അനുയോജ്യമാണ്?",
        "അപേക്ഷിക്കുന്നതിന് മുമ്പ് ഞാൻ എന്താണ് പരിശോധിക്കേണ്ടത്?",
        "എനിക്ക് ഏറ്റവും അനുയോജ്യമായ പദ്ധതി വിശദീകരിക്കാമോ?",
        "എനിക്ക് എന്തെല്ലാം രേഖകൾ ആവശ്യമായി വരാം?"
    ]
}


questions = suggested_questions.get(
    language,
    suggested_questions["English"]
)


question_cols = st.columns(
    3,
    gap="small"
)


for index, question in enumerate(
    questions
):

    with question_cols[
        index % 3
    ]:

        if st.button(
            question,
            key=f"suggestion_{index}",
            use_container_width=True
        ):

            st.session_state[
                "pending_question"
            ] = question

            st.rerun()


# ============================================================
# DIVIDER
# ============================================================

st.divider()


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state[
    "chat_history"
]:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# ============================================================
# VOICE INPUT
# ============================================================

st.markdown(
    """
    <div class="section-title">
        🎙️ Voice Question
    </div>
    """,
    unsafe_allow_html=True
)

st.caption(
    "Record your question and SchemeMatch AI "
    "will convert your speech into text."
)


audio_value = st.audio_input(
    "🎙️ Record your question"
)


voice_question = None


if audio_value is not None:

    with st.spinner(
        "🎙️ Converting speech to text..."
    ):

        try:

            # ------------------------------------------------
            # GROQ CLIENT
            # ------------------------------------------------

            client = Groq()

            audio_bytes = (
                audio_value.getvalue()
            )

            # ------------------------------------------------
            # SPEECH TO TEXT
            # ------------------------------------------------

            transcription = (
                client.audio.transcriptions.create(
                    file=(
                        "voice_question.wav",
                        audio_bytes,
                        "audio/wav"
                    ),
                    model="whisper-large-v3-turbo"
                )
            )

            voice_question = (
                transcription.text.strip()
            )

            # ------------------------------------------------
            # DISPLAY TRANSCRIPTION
            # ------------------------------------------------

            if voice_question:

                st.success(
                    "📝 Transcription"
                )

                st.info(
                    voice_question
                )

            else:

                st.warning(
                    "No speech could be detected. "
                    "Please try recording again."
                )

        except Exception as e:

            st.error(
                "Unable to convert the voice "
                "recording to text."
            )

            st.caption(
                f"Error: {str(e)}"
            )


# ============================================================
# DIVIDER
# ============================================================

st.divider()


# ============================================================
# CHAT INPUT
# ============================================================

chat_placeholder = {

    "English":
        "Ask about your recommended schemes...",

    "தமிழ்":
        "உங்களுக்கு பரிந்துரைக்கப்பட்ட திட்டங்களைப் பற்றி கேளுங்கள்...",

    "हिन्दी":
        "आपके लिए सुझाई गई योजनाओं के बारे में पूछें...",

    "മലയാളം":
        "നിങ്ങൾക്ക് ശുപാർശ ചെയ്ത പദ്ധതികളെക്കുറിച്ച് ചോദിക്കൂ..."
}


user_question = st.chat_input(
    chat_placeholder.get(
        language,
        chat_placeholder["English"]
    )
)


# ============================================================
# HANDLE VOICE QUESTION
# ============================================================

if voice_question:

    user_question = voice_question


# ============================================================
# HANDLE SUGGESTED QUESTION
# ============================================================

if (
    "pending_question"
    in st.session_state
    and not user_question
):

    user_question = (
        st.session_state.pop(
            "pending_question"
        )
    )


# ============================================================
# PROCESS QUESTION
# ============================================================

if user_question:

    # --------------------------------------------------------
    # DISPLAY USER MESSAGE
    # --------------------------------------------------------

    with st.chat_message(
        "user"
    ):

        st.markdown(
            user_question
        )

    # --------------------------------------------------------
    # SAVE USER MESSAGE
    # --------------------------------------------------------

    st.session_state[
        "chat_history"
    ].append(
        {
            "role": "user",
            "content": user_question
        }
    )

    # --------------------------------------------------------
    # GENERATE AI RESPONSE
    # --------------------------------------------------------

    with st.chat_message(
        "assistant"
    ):

        thinking_text = {

            "English":
                "Thinking...",

            "தமிழ்":
                "பதில் தயாரிக்கப்படுகிறது...",

            "हिन्दी":
                "उत्तर तैयार किया जा रहा है...",

            "മലയാളം":
                "ഉത്തരം തയ്യാറാക്കുന്നു..."
        }

        with st.spinner(
            "🤖 "
            + thinking_text.get(
                language,
                "Thinking..."
            )
        ):

            try:

                # ------------------------------------------------
                # AI RESPONSE
                # ------------------------------------------------

                answer = ask_ai(

                    profile=profile,

                    scheme_results=all_results,

                    question=user_question,

                    chat_history=(
                        st.session_state[
                            "chat_history"
                        ][:-1]
                    ),

                    language=language
                )

                # ------------------------------------------------
                # DISPLAY RESPONSE
                # ------------------------------------------------

                st.markdown(
                    answer
                )

                # ------------------------------------------------
                # SAVE AI RESPONSE
                # ------------------------------------------------

                st.session_state[
                    "chat_history"
                ].append(
                    {
                        "role": "assistant",
                        "content": answer
                    }
                )

            except Exception as e:

                st.error(
                    "Unable to generate "
                    "an AI response."
                )

                st.caption(
                    f"Error: {str(e)}"
                )
