"""
SkillLens Galaxy - Playful Resume Skill Scanner
Transform boring PDFs into a fun, visual, shareable skill profile
"""
import os
import json
import logging
import streamlit as st
from dotenv import load_dotenv
import time
from backend.security import allowed_file, validate_file_size, secure_hash_name
from backend.parser import extract_text_from_pdf
from backend.utils import load_json
from backend.skills import extract_skills, flatten_categories, coverage_against_role

# ---- Constants ----
APP_VERSION = "0.2.0-GALAXY"

# Color Palette
COLOR_PRIMARY = "#FF2E63"      # Hot Coral
COLOR_SECONDARY = "#08D9D6"    # Electric Cyan
COLOR_BG = "#0A0A1A"          # Deep Void
COLOR_CARD = "#1A1A2E"        # Navy Glass
COLOR_TEXT = "#FFFFFF"
COLOR_TEXT_SECONDARY = "#A0A0FF"  # Soft Lavender
COLOR_SUCCESS = "#00FFC6"

# ---- Logging ----
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ---- Bootstrap ----
load_dotenv()

# Custom CSS for Skill Galaxy theme
st.set_page_config(
    page_title="SkillLens Galaxy 🌌",
    layout="wide",
    page_icon="🌌",
    initial_sidebar_state="collapsed"
)

# Inject custom CSS
st.markdown(f"""
<style>
    /* Dark Void Background */
    .stApp {{
        background: linear-gradient(135deg, {COLOR_BG} 0%, #0F0F23 100%);
        color: {COLOR_TEXT};
    }}
    
    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
    /* Custom animations */
    @keyframes pulse {{
        0%, 100% {{ transform: scale(1); }}
        50% {{ transform: scale(1.05); }}
    }}
    
    @keyframes float {{
        0%, 100% {{ transform: translateY(0px); }}
        50% {{ transform: translateY(-10px); }}
    }}
    
    @keyframes glow {{
        0%, 100% {{ box-shadow: 0 0 20px {COLOR_PRIMARY}40; }}
        50% {{ box-shadow: 0 0 40px {COLOR_PRIMARY}80; }}
    }}
    
    /* Coral buttons */
    .stButton > button {{
        background: linear-gradient(135deg, {COLOR_PRIMARY} 0%, #FF1744 100%);
        color: {COLOR_TEXT};
        border: none;
        border-radius: 16px;
        padding: 16px 32px;
        font-size: 18px;
        font-weight: bold;
        transition: all 0.3s ease;
        animation: pulse 2s infinite;
    }}
    
    .stButton > button:hover {{
        transform: scale(1.05);
        box-shadow: 0 8px 30px {COLOR_PRIMARY}60;
    }}
    
    /* File uploader styling */
    .uploadedFile {{
        background: {COLOR_CARD} !important;
        border: 2px dashed {COLOR_SECONDARY} !important;
        border-radius: 16px !important;
        animation: glow 3s infinite;
    }}
    
    /* Cards */
    .skill-card {{
        background: {COLOR_CARD};
        border-radius: 20px;
        padding: 24px;
        margin: 16px 0;
        border: 1px solid {COLOR_SECONDARY}30;
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
        transition: all 0.3s ease;
    }}
    
    .skill-card:hover {{
        transform: translateY(-5px);
        border-color: {COLOR_SECONDARY};
        box-shadow: 0 12px 48px {COLOR_SECONDARY}40;
    }}
    
    /* Skill orbs */
    .skill-orb {{
        display: inline-block;
        background: linear-gradient(135deg, {COLOR_PRIMARY}, {COLOR_SECONDARY});
        color: {COLOR_TEXT};
        padding: 12px 24px;
        margin: 8px;
        border-radius: 50px;
        font-weight: 600;
        font-size: 14px;
        box-shadow: 0 4px 16px rgba(8, 217, 214, 0.4);
        transition: all 0.3s ease;
        cursor: pointer;
        animation: float 3s ease-in-out infinite;
    }}
    
    .skill-orb:hover {{
        transform: scale(1.1);
        box-shadow: 0 8px 24px {COLOR_SECONDARY}80;
    }}
    
    /* Typography */
    h1, h2, h3 {{
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        background: linear-gradient(135deg, {COLOR_PRIMARY}, {COLOR_SECONDARY});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    
    /* Progress bar */
    .stProgress > div > div > div {{
        background: linear-gradient(90deg, {COLOR_PRIMARY}, {COLOR_SECONDARY});
    }}
    
    /* Success message */
    .success-banner {{
        background: linear-gradient(135deg, {COLOR_SUCCESS}20, {COLOR_SECONDARY}20);
        border-left: 4px solid {COLOR_SUCCESS};
        padding: 20px;
        border-radius: 12px;
        margin: 20px 0;
        animation: pulse 1s ease-in-out;
    }}
    
    /* Galaxy effect */
    .galaxy-title {{
        font-size: 64px;
        text-align: center;
        margin: 40px 0;
        animation: float 4s ease-in-out infinite;
    }}
    
    /* Stat badges */
    .stat-badge {{
        background: {COLOR_CARD};
        border: 2px solid {COLOR_PRIMARY};
        border-radius: 16px;
        padding: 16px;
        text-align: center;
        min-width: 120px;
    }}
    
    .stat-number {{
        font-size: 48px;
        font-weight: bold;
        background: linear-gradient(135deg, {COLOR_PRIMARY}, {COLOR_SECONDARY});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    
    .stat-label {{
        color: {COLOR_TEXT_SECONDARY};
        font-size: 14px;
        margin-top: 8px;
    }}
</style>
""", unsafe_allow_html=True)

# ---- Session State ----
if "analysis_count" not in st.session_state:
    st.session_state.analysis_count = 0
if "skill_streak" not in st.session_state:
    st.session_state.skill_streak = 0
if "total_skills_found" not in st.session_state:
    st.session_state.total_skills_found = 0
if "confetti_triggered" not in st.session_state:
    st.session_state.confetti_triggered = False

# ---- Load Data ----
@st.cache_data
def _load_roles():
    return load_json("data/roles.json")

@st.cache_data
def _load_skill_bank():
    return load_json("data/skill_bank.json")

roles = _load_roles()
skill_bank = _load_skill_bank()

# ---- UI ----
# Galaxy Title
st.markdown("""
<div class="galaxy-title">
    🌌 SkillLens Galaxy
</div>
<p style='text-align: center; color: {COLOR_TEXT_SECONDARY}; font-size: 20px; margin-bottom: 60px;'>
    Turn your resume into a constellation of skills
</p>
""".format(COLOR_TEXT_SECONDARY=COLOR_TEXT_SECONDARY), unsafe_allow_html=True)

# Upload Section - "Drop your resume like it's hot"
st.markdown("""
<div style='text-align: center; margin: 40px 0;'>
    <h2 style='font-size: 32px;'>🔥 Drop your resume like it's hot</h2>
    <p style='color: {COLOR_TEXT_SECONDARY}; font-size: 16px;'>We'll roast it and extract your skill DNA</p>
</div>
""".format(COLOR_TEXT_SECONDARY=COLOR_TEXT_SECONDARY), unsafe_allow_html=True)

col_upload, col_role = st.columns([2, 1])

with col_upload:
    uploaded = st.file_uploader(
        "📄 PDF only, max 5 MB",
        type=["pdf"],
        label_visibility="collapsed"
    )

with col_role:
    target_role = st.selectbox(
        "🎯 Target Role",
        options=list(roles.keys()),
        label_visibility="collapsed"
    )

# Analyze button - playful copy
analyze_disabled = uploaded is None or st.session_state.analysis_count >= 10

st.markdown("<div style='text-align: center; margin: 30px 0;'>", unsafe_allow_html=True)
analyze = st.button(
    "🚀 Launch Skill Analysis",
    type="primary",
    disabled=analyze_disabled,
    use_container_width=False
)
st.markdown("</div>", unsafe_allow_html=True)

if st.session_state.analysis_count >= 10:
    st.error("🎮 Level limit reached! Refresh to continue your skill journey.")

# ---- Analysis Logic ----
if analyze and uploaded:
    # Confetti effect
    if not st.session_state.confetti_triggered:
        st.balloons()
        st.session_state.confetti_triggered = True
    
    # Validate file
    mime = uploaded.type
    fname = uploaded.name
    data = uploaded.read()
    
    if not allowed_file(fname, mime):
        st.error("❌ PDFs only! We can't read minds... yet.")
        st.stop()
    
    if not validate_file_size(data):
        st.error(f"📦 Whoa! That's {len(data) / (1024*1024):.1f} MB. Keep it under 5 MB please!")
        st.stop()
    
    safe_name = secure_hash_name(fname)
    logger.info(f"Galaxy analysis started | file={fname}")
    
    # Progress with personality
    progress_messages = [
        ("Extracting skills... 👀", 0.2),
        ("Roasting your resume... 🔥", 0.5),
        ("Mapping your skill constellation... ✨", 0.8),
        ("Skill DNA ready! 🧬", 1.0)
    ]
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for msg, progress in progress_messages:
        status_text.markdown(f"**{msg}**")
        progress_bar.progress(progress)
        time.sleep(0.5)
    
    # Extract text
    try:
        text = extract_text_from_pdf(data)
    except Exception as e:
        st.error(f"💥 PDF parsing failed: {str(e)}")
        logger.error(f"PDF parsing failed: {fname} - {str(e)}")
        st.stop()
    
    char_count = len(text or "")
    word_count = len((text or "").split())
    
    if char_count == 0:
        st.error("👻 Empty resume detected! Add some content first.")
        st.stop()
    
    # Extract skills
    extracted = extract_skills(text, skill_bank)
    flat = flatten_categories(extracted)
    
    # Coverage calculation
    role_skills = roles.get(target_role, [])
    coverage, missing = coverage_against_role(flat, role_skills)
    
    # Update stats
    st.session_state.analysis_count += 1
    st.session_state.skill_streak += 1
    st.session_state.total_skills_found += len(flat)
    
    logger.info(f"Galaxy analysis complete | skills={len(flat)} | coverage={coverage}%")
    
    progress_bar.empty()
    status_text.empty()
    
    # Success banner
    st.markdown(f"""
    <div class="success-banner">
        <h2 style='margin: 0; font-size: 28px;'>🎉 Skill Galaxy Mapped!</h2>
        <p style='margin: 10px 0 0 0; color: {COLOR_TEXT_SECONDARY};'>
            Discovered {len(flat)} unique skills across your resume universe
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats Dashboard
    st.markdown("### 📊 Your Skill Stats")
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
    
    with stat_col1:
        st.markdown(f"""
        <div class="stat-badge">
            <div class="stat-number">{coverage}%</div>
            <div class="stat-label">Role Match</div>
        </div>
        """, unsafe_allow_html=True)
    
    with stat_col2:
        st.markdown(f"""
        <div class="stat-badge">
            <div class="stat-number">{len(flat)}</div>
            <div class="stat-label">Skills Found</div>
        </div>
        """, unsafe_allow_html=True)
    
    with stat_col3:
        st.markdown(f"""
        <div class="stat-badge">
            <div class="stat-number">{st.session_state.skill_streak}</div>
            <div class="stat-label">Streak 🔥</div>
        </div>
        """, unsafe_allow_html=True)
    
    with stat_col4:
        st.markdown(f"""
        <div class="stat-badge">
            <div class="stat-number">{len([c for c in extracted.values() if c])}</div>
            <div class="stat-label">Categories</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Skill Galaxy - Skills as orbs
    st.markdown("""
    <div class="skill-card">
        <h2 style='margin-top: 0;'>🌟 Your Skill Constellation</h2>
        <p style='color: {COLOR_TEXT_SECONDARY}; margin-bottom: 24px;'>
            Hover over skills to see them glow
        </p>
    """.format(COLOR_TEXT_SECONDARY=COLOR_TEXT_SECONDARY), unsafe_allow_html=True)
    
    for category, skills in extracted.items():
        if skills:
            st.markdown(f"**{category.replace('_', ' ').title()}**")
            orbs_html = " ".join([
                f'<span class="skill-orb" title="Found in resume">{skill}</span>'
                for skill in sorted(skills)
            ])
            st.markdown(orbs_html, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Missing Skills - with personality
    if missing:
        st.markdown(f"""
        <div class="skill-card">
            <h2 style='margin-top: 0;'>🤖 Skills to Level Up</h2>
            <p style='color: {COLOR_TEXT_SECONDARY};'>
                Add these to unlock the full {target_role} achievement
            </p>
            <br>
        """, unsafe_allow_html=True)
        
        missing_orbs = " ".join([
            f'<span class="skill-orb" style="opacity: 0.5; background: linear-gradient(135deg, #666, #999);">{skill}</span>'
            for skill in sorted(missing[:10])
        ])
        st.markdown(missing_orbs, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Shareable Skill Card
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🎴 Share Your Skills")
    
    col_share1, col_share2 = st.columns([2, 1])
    
    with col_share1:
        # Top 3 skills card
        top_3_skills = flat[:3] if len(flat) >= 3 else flat
        st.markdown(f"""
        <div class="skill-card" style="background: linear-gradient(135deg, {COLOR_PRIMARY}20, {COLOR_SECONDARY}20);">
            <h3>🏆 Top Skills</h3>
        """, unsafe_allow_html=True)
        for i, skill in enumerate(top_3_skills, 1):
            st.markdown(f"**{i}.** {skill}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col_share2:
        # Download JSON result
        result = {
            "target_role": target_role,
            "coverage": coverage,
            "skills_found": len(flat),
            "missing_skills": missing,
            "extracted_by_category": extracted,
            "extracted_flat_unique": flat,
            "stats": {
                "streak": st.session_state.skill_streak,
                "total_analyses": st.session_state.analysis_count,
                "app_version": APP_VERSION
            }
        }
        
        st.download_button(
            "💾 Save Galaxy Data",
            data=json.dumps(result, indent=2),
            file_name=f"skill_galaxy_{safe_name}.json",
            mime="application/json",
            use_container_width=True
        )

# Footer - with personality
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(f"""
<div style='text-align: center; color: {COLOR_TEXT_SECONDARY}; padding: 40px 0;'>
    <p style='font-size: 14px;'>
        Made with 💜 by SkillLens Galaxy v{APP_VERSION}<br>
        No data stored • All processing happens locally<br>
        <a href='https://github.com/Ansh2610/TODO-list-web' target='_blank' style='color: {COLOR_PRIMARY}; text-decoration: none;'>
            ⭐ Star on GitHub
        </a>
    </p>
</div>
""", unsafe_allow_html=True)
