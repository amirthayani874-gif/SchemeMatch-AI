import streamlit as st
import pandas as pd

from modules.translations import (
    render_language_selector,
    t,
    scheme_text
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Compare Schemes | SchemeMatch AI",
    page_icon="⚖️",
    layout="wide"
)


# ============================================================
# LANGUAGE
# ============================================================

render_language_selector()


# ============================================================
# TRANSLATIONS FOR COMPARISON PAGE
# ============================================================

COMPARE_TRANSLATIONS = {

    "English": {
        "title": "⚖️ Compare Schemes",
        "description": "Compare your top two recommended schemes and understand the key differences.",
        "comparison": "📊 Scheme Comparison",
        "feature": "Feature",
        "top_scheme": "🥇 Top Scheme",
        "second_scheme": "🥈 Second Scheme",
        "match_score": "Match Score",
        "benefit_type": "Benefit Type",
        "benefit_description": "Benefit Description",
        "official": "🔗 Official Information",
        "view_official": "🔗 View Official Information",
        "no_profile": "Please create your entrepreneur profile and find your schemes first.",
        "go_find": "🎯 Go to Find My Schemes",
        "not_enough": "At least two matched schemes are required for comparison.",
        "disclaimer": "⚠️ Match scores are prototype recommendations based on the information you provided. They are not an official eligibility decision. Please verify the latest requirements on the official government portal."
    },

    "தமிழ்": {
        "title": "⚖️ திட்டங்களை ஒப்பிடுக",
        "description": "உங்கள் முதல் இரண்டு பரிந்துரைக்கப்பட்ட திட்டங்களை ஒப்பிட்டு முக்கிய வேறுபாடுகளைப் புரிந்துகொள்ளுங்கள்.",
        "comparison": "📊 திட்ட ஒப்பீடு",
        "feature": "விவரம்",
        "top_scheme": "🥇 முதல் திட்டம்",
        "second_scheme": "🥈 இரண்டாவது திட்டம்",
        "match_score": "பொருத்த மதிப்பெண்",
        "benefit_type": "நன்மை வகை",
        "benefit_description": "நன்மை விளக்கம்",
        "official": "🔗 அதிகாரப்பூர்வ தகவல்",
        "view_official": "🔗 அதிகாரப்பூர்வ தகவலைப் பார்க்கவும்",
        "no_profile": "முதலில் உங்கள் தொழில்முனைவோர் சுயவிவரத்தை உருவாக்கி திட்டங்களைக் கண்டறியவும்.",
        "go_find": "🎯 எனக்கான திட்டங்களை கண்டறியவும்",
        "not_enough": "ஒப்பிடுவதற்கு குறைந்தது இரண்டு பொருத்தமான திட்டங்கள் தேவை.",
        "disclaimer": "⚠️ பொருத்த மதிப்பெண்கள் நீங்கள் வழங்கிய தகவலின் அடிப்படையிலான மாதிரி பரிந்துரைகள் மட்டுமே. இவை அதிகாரப்பூர்வ தகுதி முடிவு அல்ல. சமீபத்திய தேவைகளை அதிகாரப்பூர்வ அரசு இணையதளத்தில் சரிபார்க்கவும்."
    },

    "हिन्दी": {
        "title": "⚖️ योजनाओं की तुलना करें",
        "description": "अपनी शीर्ष दो अनुशंसित योजनाओं की तुलना करें और मुख्य अंतर समझें।",
        "comparison": "📊 योजना तुलना",
        "feature": "विवरण",
        "top_scheme": "🥇 पहली योजना",
        "second_scheme": "🥈 दूसरी योजना",
        "match_score": "मैच स्कोर",
        "benefit_type": "लाभ का प्रकार",
        "benefit_description": "लाभ का विवरण",
        "official": "🔗 आधिकारिक जानकारी",
        "view_official": "🔗 आधिकारिक जानकारी देखें",
        "no_profile": "कृपया पहले अपनी उद्यमी प्रोफ़ाइल बनाएँ और योजनाएँ खोजें।",
        "go_find": "🎯 मेरी योजनाएँ खोजें",
        "not_enough": "तुलना के लिए कम से कम दो मिलान वाली योजनाएँ आवश्यक हैं।",
        "disclaimer": "⚠️ मैच स्कोर आपके द्वारा दी गई जानकारी के आधार पर केवल प्रोटोटाइप सिफारिशें हैं। यह आधिकारिक पात्रता निर्णय नहीं है। नवीनतम आवश्यकताओं की पुष्टि आधिकारिक सरकारी पोर्टल पर करें।"
    },

    "മലയാളം": {
        "title": "⚖️ പദ്ധതികൾ താരതമ്യം ചെയ്യുക",
        "description": "നിങ്ങളുടെ മികച്ച രണ്ട് ശുപാർശ ചെയ്ത പദ്ധതികളെ താരതമ്യം ചെയ്ത് പ്രധാന വ്യത്യാസങ്ങൾ മനസ്സിലാക്കുക.",
        "comparison": "📊 പദ്ധതി താരതമ്യം",
        "feature": "വിവരം",
        "top_scheme": "🥇 ആദ്യ പദ്ധതി",
        "second_scheme": "🥈 രണ്ടാമത്തെ പദ്ധതി",
        "match_score": "പൊരുത്ത സ്കോർ",
        "benefit_type": "പ്രയോജന തരം",
        "benefit_description": "പ്രയോജന വിശദീകരണം",
        "official": "🔗 ഔദ്യോഗിക വിവരങ്ങൾ",
        "view_official": "🔗 ഔദ്യോഗിക വിവരങ്ങൾ കാണുക",
        "no_profile": "ആദ്യം നിങ്ങളുടെ സംരംഭക പ്രൊഫൈൽ സൃഷ്ടിച്ച് പദ്ധതികൾ കണ്ടെത്തുക.",
        "go_find": "🎯 എന്റെ പദ്ധതികൾ കണ്ടെത്തുക",
        "not_enough": "താരതമ്യത്തിനായി കുറഞ്ഞത് രണ്ട് പൊരുത്തപ്പെടുന്ന പദ്ധതികൾ ആവശ്യമാണ്.",
        "disclaimer": "⚠️ പൊരുത്ത സ്കോറുകൾ നിങ്ങൾ നൽകിയ വിവരങ്ങളുടെ അടിസ്ഥാനത്തിലുള്ള പ്രോട്ടോടൈപ്പ് ശുപാർശകൾ മാത്രമാണ്. ഇത് ഔദ്യോഗിക യോഗ്യതാ തീരുമാനം അല്ല. ഏറ്റവും പുതിയ ആവശ്യകതകൾ ഔദ്യോഗിക സർക്കാർ പോർട്ടലിൽ പരിശോധിക്കുക."
    }
}


# ============================================================
# HELPER
# ============================================================

def ct(key):

    language = st.session_state.get(
        "language",
        "English"
    )

    return COMPARE_TRANSLATIONS.get(
        language,
        COMPARE_TRANSLATIONS["English"]
    ).get(
        key,
        COMPARE_TRANSLATIONS["English"].get(key, key)
    )


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
<style>

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}

.page-title {
    font-size: 2.4rem;
    font-weight: 700;
    color: #202638;
    margin-bottom: 0.4rem;
}

.page-description {
    font-size: 1rem;
    color: #5d687d;
    margin-bottom: 2rem;
    line-height: 1.6;
}

.section-title {
    font-size: 1.45rem;
    font-weight: 650;
    color: #202638;
    margin-top: 1.5rem;
    margin-bottom: 1rem;
}

.scheme-name {
    font-size: 1.05rem;
    font-weight: 650;
    color: #202638;
    line-height: 1.5;
    margin-bottom: 0.8rem;
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
    min-height: 2.8rem;
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
    f"""
<div class="page-title">
{ct("title")}
</div>

<div class="page-description">
{ct("description")}
</div>
""",
    unsafe_allow_html=True
)


# ============================================================
# CHECK PROFILE
# ============================================================

if "profile" not in st.session_state:

    st.warning(
        f"⚠️ {ct('no_profile')}"
    )

    if st.button(
        ct("go_find"),
        use_container_width=True
    ):
        st.switch_page(
            "pages/1_Find_Schemes.py"
        )

    st.stop()


# ============================================================
# GET RESULTS
# ============================================================

results = st.session_state.get(
    "results",
    []
)


if len(results) < 2:

    st.warning(
        f"⚠️ {ct('not_enough')}"
    )

    st.stop()


top_scheme = results[0]
second_scheme = results[1]


# ============================================================
# COMPARISON TITLE
# ============================================================

st.markdown(
    f"""
<div class="section-title">
{ct("comparison")}
</div>
""",
    unsafe_allow_html=True
)


# ============================================================
# SCHEME NAMES
# ============================================================

col1, col2 = st.columns(
    2,
    gap="large"
)


with col1:

    st.markdown(
        f"""
<div class="scheme-name">
🥇 {ct("top_scheme")}<br>
{scheme_text(top_scheme["scheme_name"])}
</div>
""",
        unsafe_allow_html=True
    )


with col2:

    st.markdown(
        f"""
<div class="scheme-name">
🥈 {ct("second_scheme")}<br>
{scheme_text(second_scheme["scheme_name"])}
</div>
""",
        unsafe_allow_html=True
    )


# ============================================================
# CLEAN COMPARISON TABLE
# ============================================================

comparison_data = {

    ct("feature"): [
        ct("match_score"),
        ct("benefit_type"),
        ct("benefit_description")
    ],

    ct("top_scheme"): [
        f"{top_scheme['score']}%",
        scheme_text(top_scheme["benefit_type"]),
        scheme_text(top_scheme["benefit_description"])
    ],

    ct("second_scheme"): [
        f"{second_scheme['score']}%",
        scheme_text(second_scheme["benefit_type"]),
        scheme_text(second_scheme["benefit_description"])
    ]
}


comparison_df = pd.DataFrame(
    comparison_data
)


st.table(
    comparison_df
)


# ============================================================
# OFFICIAL INFORMATION
# ============================================================

st.markdown(
    f"""
<div class="section-title">
{ct("official")}
</div>
""",
    unsafe_allow_html=True
)


official_col1, official_col2 = st.columns(
    2,
    gap="large"
)


with official_col1:

    st.markdown(
        f"**🥇 {scheme_text(top_scheme['scheme_name'])}**"
    )

    st.link_button(
        ct("view_official"),
        top_scheme["official_url"],
        use_container_width=True
    )


with official_col2:

    st.markdown(
        f"**🥈 {scheme_text(second_scheme['scheme_name'])}**"
    )

    st.link_button(
        ct("view_official"),
        second_scheme["official_url"],
        use_container_width=True
    )


# ============================================================
# DISCLAIMER
# ============================================================

st.markdown(
    f"""
<div class="disclaimer">
{ct("disclaimer")}
</div>
""",
    unsafe_allow_html=True
)