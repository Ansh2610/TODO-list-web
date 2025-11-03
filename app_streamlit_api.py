"""
SkillLens Galaxy - API-Powered Frontend
Streamlit app that consumes FastAPI backend for all operations
"""
import os
import logging
import streamlit as st
import time
import atexit
import tempfile
from pathlib import Path
import httpx

from api.client import get_api_client

# ---- Constants ----
APP_VERSION = "0.3.0-API"
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

# ---- Logging ----
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ---- Cleanup Handler ----
def cleanup_on_exit():
    """Clean up resources when app closes"""
    logger.info("🌌 SkillLens Galaxy shutting down gracefully...")

atexit.register(cleanup_on_exit)

# Color Palette (same as original)
COLOR_PRIMARY = "#FF2E63"
COLOR_SECONDARY = "#08D9D6"
COLOR_BG = "#0A0A1A"
COLOR_CARD = "#1A1A2E"
COLOR_TEXT = "#FFFFFF"
COLOR_TEXT_SECONDARY = "#A0A0FF"
COLOR_SUCCESS = "#00FFC6"

# ---- Page Config ----
st.set_page_config(
    page_title="SkillLens Galaxy 🌌",
    layout="wide",
    page_icon="🌌",
    initial_sidebar_state="collapsed"
)

# ---- Inject CSS (same styling as original) ----
st.markdown(f"""
<style>
    .stApp {{
        background: linear-gradient(135deg, {COLOR_BG} 0%, #0F0F23 100%);
        color: {COLOR_TEXT};
    }}
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
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
    
    h1, h2, h3 {{
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        background: linear-gradient(135deg, {COLOR_PRIMARY}, {COLOR_SECONDARY});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    
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
        font-size: 14px;
        color: {COLOR_TEXT_SECONDARY};
        margin-top: 8px;
    }}
    
    .success-banner {{
        background: linear-gradient(135deg, {COLOR_SUCCESS}20, {COLOR_SECONDARY}20);
        border-left: 4px solid {COLOR_SUCCESS};
        padding: 20px;
        border-radius: 12px;
        margin: 20px 0;
        animation: pulse 1s ease-in-out;
    }}
</style>
""", unsafe_allow_html=True)

# ---- Session State Initialization ----
if "analysis_count" not in st.session_state:
    st.session_state.analysis_count = 0
if "skill_streak" not in st.session_state:
    st.session_state.skill_streak = 0
if "total_skills_found" not in st.session_state:
    st.session_state.total_skills_found = 0
if "ai_insights_used" not in st.session_state:
    st.session_state.ai_insights_used = 0
if "current_results" not in st.session_state:
    st.session_state.current_results = None
if "ai_recommendations" not in st.session_state:
    st.session_state.ai_recommendations = None
if "ai_error" not in st.session_state:
    st.session_state.ai_error = None

# ---- Initialize API Client ----
api_client = get_api_client(API_BASE_URL)

# ---- Check API Health ----
try:
    health = api_client.health_check()
    logger.info(f"✅ Connected to API v{health['version']}")
except Exception as e:
    st.error(f"""
    🚨 **Cannot connect to FastAPI backend!**
    
    Please start the API server first:
    ```bash
    uvicorn api.main:app --reload
    ```
    
    Error: {str(e)}
    """)
    st.stop()

# ---- Header ----
st.markdown(f"""
<div style='text-align: center; padding: 40px 0;'>
    <div class='galaxy-title'>🌌 SkillLens Galaxy</div>
    <p style='font-size: 20px; color: {COLOR_TEXT_SECONDARY}; margin-top: -20px;'>
        Transform your resume into a visual skill profile
    </p>
    <p style='font-size: 14px; color: {COLOR_TEXT_SECONDARY}; opacity: 0.7;'>
        Powered by FastAPI • v{APP_VERSION}
    </p>
</div>
""", unsafe_allow_html=True)

# ---- Main Upload Section ----
st.markdown("""
<div class="skill-card">
    <h2 style='margin-top: 0;'>📄 Upload Your Resume</h2>
    <p style='color: {COLOR_TEXT_SECONDARY};'>
        Drop a PDF (max 5 MB) and let's analyze your skill constellation
    </p>
</div>
""".format(COLOR_TEXT_SECONDARY=COLOR_TEXT_SECONDARY), unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Choose a PDF resume",
    type=["pdf"],
    help="Max 5 MB, PDF format only",
    label_visibility="collapsed"
)

# Get available roles from API
try:
    roles_response = api_client.get_roles()
    available_roles = roles_response["roles"]
except Exception as e:
    logger.error(f"Failed to fetch roles: {e}")
    available_roles = ["Software Engineer", "Data Scientist", "Product Manager"]

target_role = st.selectbox(
    "🎯 Target Role",
    available_roles,
    help="Select the job role you're targeting"
)

# ---- Analysis Section ----
if uploaded_file is not None:
    if st.button("🚀 Analyze My Skills", use_container_width=True):
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        try:
            # Progress animation
            progress_messages = [
                ("Uploading to API... 📤", 0.2),
                ("Extracting skills... 👀", 0.5),
                ("Benchmarking against role... 📊", 0.8),
                ("Skill DNA ready! 🧬", 1.0)
            ]
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for msg, progress in progress_messages:
                status_text.markdown(f"**{msg}**")
                progress_bar.progress(progress)
                time.sleep(0.5)
            
            # Step 1: Parse PDF via API
            parse_result = api_client.parse_resume(tmp_path)
            
            if not parse_result["success"]:
                st.error(f"❌ {parse_result['error']}")
                st.stop()
            
            skills = parse_result["skills"]
            logger.info(f"✓ Parsed resume: {len(skills)} skills found")
            
            # Step 2: Benchmark via API
            benchmark_result = api_client.benchmark_skills(
                resume_skills=skills,
                target_role=target_role
            )
            
            if not benchmark_result["success"]:
                st.error(f"❌ {benchmark_result['error']}")
                st.stop()
            
            coverage = benchmark_result["coverage_percentage"]
            found_skills = benchmark_result["found_skills"]
            missing_skills = benchmark_result["missing_skills"]
            
            logger.info(f"✓ Benchmark complete: {coverage:.1f}% coverage")
            
            # Update session state stats
            st.session_state.analysis_count += 1
            st.session_state.skill_streak += 1
            st.session_state.total_skills_found += len(skills)
            
            # Store results
            st.session_state.current_results = {
                "skills": skills,
                "found_skills": found_skills,
                "missing_skills": missing_skills,
                "coverage": coverage,
                "target_role": target_role
            }
            
            # Clear progress
            progress_bar.empty()
            status_text.empty()
            
            # Success message
            st.markdown(f"""
            <div class="success-banner">
                <h2 style='margin: 0; color: {COLOR_SUCCESS};'>✨ Analysis Complete!</h2>
                <p style='margin: 8px 0 0 0; font-size: 18px;'>
                    Found {len(skills)} skills • {coverage:.1f}% match with {target_role}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
        except httpx.HTTPError as e:
            st.error(f"🌐 **API Error:** {str(e)}")
            logger.error(f"API call failed: {e}")
        except Exception as e:
            st.error(f"💥 **Unexpected error:** {str(e)}")
            logger.error(f"Analysis failed: {e}", exc_info=True)
        finally:
            # Clean up temp file
            Path(tmp_path).unlink(missing_ok=True)

# ---- Display Results (if available in session state) ----
if st.session_state.current_results is not None:
    results = st.session_state.current_results
    
    # Stats Dashboard
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
    
    with stat_col1:
        st.markdown(f"""
        <div class="stat-badge">
            <div class="stat-number">{results['coverage']:.0f}%</div>
            <div class="stat-label">Coverage</div>
        </div>
        """, unsafe_allow_html=True)
    
    with stat_col2:
        st.markdown(f"""
        <div class="stat-badge">
            <div class="stat-number">{len(results['skills'])}</div>
            <div class="stat-label">Total Skills</div>
        </div>
        """, unsafe_allow_html=True)
    
    with stat_col3:
        st.markdown(f"""
        <div class="stat-badge">
            <div class="stat-number">{len(results['found_skills'])}</div>
            <div class="stat-label">Matched</div>
        </div>
        """, unsafe_allow_html=True)
    
    with stat_col4:
        st.markdown(f"""
        <div class="stat-badge">
            <div class="stat-number">{len(results['missing_skills'])}</div>
            <div class="stat-label">Missing</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Skills Display
    st.markdown(f"""
    <div class="skill-card">
        <h2 style='margin-top: 0;'>🌟 Your Skill Constellation</h2>
        <p style='color: {COLOR_TEXT_SECONDARY}; margin-bottom: 24px;'>
            All extracted skills from your resume
        </p>
    """, unsafe_allow_html=True)
    
    orbs_html = " ".join([
        f'<span class="skill-orb" title="Found in resume">{skill}</span>'
        for skill in sorted(results['skills'])
    ])
    st.markdown(orbs_html, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Missing Skills
    if results['missing_skills']:
        st.markdown(f"""
        <div class="skill-card">
            <h2 style='margin-top: 0;'>🤖 Skills to Level Up</h2>
            <p style='color: {COLOR_TEXT_SECONDARY};'>
                Add these to unlock the full {results['target_role']} achievement
            </p>
            <br>
        """, unsafe_allow_html=True)
        
        missing_orbs = " ".join([
            f'<span class="skill-orb" style="opacity: 0.5; background: linear-gradient(135deg, #666, #999);">{skill}</span>'
            for skill in sorted(results['missing_skills'][:10])
        ])
        st.markdown(missing_orbs, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # AI Insights Section
    st.markdown(f"""
    <div class="skill-card">
        <h2 style='margin-top: 0;'>🤖 AI-Powered Career Insights</h2>
        <p style='color: {COLOR_TEXT_SECONDARY};'>
            Get personalized recommendations from our AI career advisor
        </p>
    """, unsafe_allow_html=True)
    
    ai_remaining = 5 - st.session_state.ai_insights_used
    
    if st.session_state.ai_insights_used >= 5:
        st.warning("⚠️ You've used all 5 AI insights for this session. Refresh to reset.")
    else:
        if st.button(f"✨ Get AI Insights ({ai_remaining}/5 remaining)", use_container_width=True):
            try:
                with st.spinner("🧠 AI analyzing your career trajectory..."):
                    ai_result = api_client.get_ai_insights(
                        found_skills=results['found_skills'],
                        missing_skills=results['missing_skills'],
                        target_role=results['target_role'],
                        coverage_percentage=results['coverage']
                    )
                
                if ai_result["success"]:
                    st.session_state.ai_recommendations = ai_result
                    st.session_state.ai_insights_used += 1
                    st.session_state.ai_error = None
                    st.rerun()
                else:
                    st.session_state.ai_error = ai_result.get("error", "Unknown error")
            except Exception as e:
                st.session_state.ai_error = str(e)
                logger.error(f"AI insights failed: {e}")
    
    # Display AI error if exists
    if st.session_state.ai_error:
        col_err, col_btn = st.columns([4, 1])
        with col_err:
            st.error(f"❌ {st.session_state.ai_error}")
        with col_btn:
            if st.button("✕ Clear"):
                st.session_state.ai_error = None
                st.rerun()
    
    # Display AI recommendations if available
    if st.session_state.ai_recommendations:
        recs = st.session_state.ai_recommendations
        
        st.success(f"✅ AI recommendations generated via {recs.get('provider_used', 'LLM')}")
        
        # Coverage Explanation
        st.markdown(f"""
        <div class="skill-card">
            <h3 style='margin-top: 0;'>📊 Coverage Analysis</h3>
            <p>{recs['coverage_explanation']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Top Missing Skills
        st.markdown(f"""
        <div class="skill-card">
            <h3 style='margin-top: 0;'>🎯 Priority Skills</h3>
            <p>{recs['top_missing_skills']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Learning Path
        st.markdown(f"""
        <div class="skill-card">
            <h3 style='margin-top: 0;'>📚 Learning Roadmap</h3>
            <p>{recs['learning_path']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Project Ideas
        st.markdown(f"""
        <div class="skill-card">
            <h3 style='margin-top: 0;'>💡 Project Suggestions</h3>
            <p>{recs['project_ideas']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Resume Tweaks
        st.markdown(f"""
        <div class="skill-card">
            <h3 style='margin-top: 0;'>✍️ Resume Optimization</h3>
            <p>{recs['resume_tweaks']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# ---- Footer ----
st.markdown(f"""
<div style='text-align: center; padding: 40px 0; color: {COLOR_TEXT_SECONDARY}; opacity: 0.5;'>
    <p>Made with 💜 by SkillLens • Analyses: {st.session_state.analysis_count} • Skills Found: {st.session_state.total_skills_found}</p>
</div>
""", unsafe_allow_html=True)
