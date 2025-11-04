"""
SkillLens - Simple & Clean Resume Analyzer
Milestone 4: Custom JD, PDF Preview, Learn Links, Export
"""
import os
import logging
import streamlit as st
import time
import tempfile
import base64
from pathlib import Path
import httpx
import json

from api.client import get_api_client
from backend.flags import (
    ENABLE_EXPORT_REPORT, 
    ENABLE_PDF_PREVIEW,
    MAX_AI_RUNS_PER_SESSION,
    MAX_ANALYSES_PER_SESSION
)

# ---- Configuration ----
APP_VERSION = "0.4.0"
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

# ---- Logging ----
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---- Page Config ----
st.set_page_config(
    page_title="SkillLens - Resume Analyzer",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="collapsed",
    menu_items={
        'About': f"SkillLens v{APP_VERSION} - Privacy-first resume skill analyzer"
    }
)

# ---- Simple Custom CSS ----
st.markdown("""
<style>
    /* Main Layout */
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #6366F1;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    
    /* Cards & Metrics */
    .metric-card {
        background: #f0f2f6;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #6366F1;
    }
    
    /* Skill Tags */
    .skill-tag {
        display: inline-block;
        background: #DBEAFE;
        color: #1E40AF;
        padding: 0.4rem 0.8rem;
        margin: 0.3rem;
        border-radius: 16px;
        font-size: 0.9rem;
    }
    .missing-skill-tag {
        display: inline-block;
        background: #FEF3C7;
        color: #92400E;
        padding: 0.4rem 0.8rem;
        margin: 0.3rem;
        border-radius: 16px;
        font-size: 0.9rem;
    }
    
    /* Learn Link */
    .learn-link {
        display: inline-block;
        background: #F0F9FF;
        color: #0EA5E9;
        padding: 0.3rem 0.6rem;
        margin-left: 0.5rem;
        border-radius: 12px;
        font-size: 0.85rem;
        text-decoration: none;
        border: 1px solid #BAE6FD;
    }
    .learn-link:hover {
        background: #E0F2FE;
    }
    
    /* Status Boxes */
    .success-box {
        background: #e8f5e9;
        border-left: 4px solid #4caf50;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .error-box {
        background: #ffebee;
        border-left: 4px solid #f44336;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    
    /* PDF Preview */
    .pdf-preview-container {
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        overflow: hidden;
        height: 600px;
    }
    
    /* Footer */
    .privacy-footer {
        text-align: center;
        padding: 2rem 1rem;
        background: #F9FAFB;
        border-top: 1px solid #E5E7EB;
        margin-top: 3rem;
        border-radius: 8px;
    }
    
    /* Responsive */
    @media (max-width: 900px) {
        .main-header { font-size: 2rem; }
        .pdf-preview-container { height: 400px; }
    }
</style>
""", unsafe_allow_html=True)

# ---- Session State ----
if "analysis_count" not in st.session_state:
    st.session_state.analysis_count = 0
if "ai_insights_used" not in st.session_state:
    st.session_state.ai_insights_used = 0
if "current_results" not in st.session_state:
    st.session_state.current_results = None
if "ai_recommendations" not in st.session_state:
    st.session_state.ai_recommendations = None
if "uploaded_pdf_bytes" not in st.session_state:
    st.session_state.uploaded_pdf_bytes = None
if "learn_links_cache" not in st.session_state:
    st.session_state.learn_links_cache = None
if "use_custom_jd" not in st.session_state:
    st.session_state.use_custom_jd = False

# ---- Initialize API Client ----
api_client = get_api_client(API_BASE_URL)

# ---- Check API Health ----
try:
    health = api_client.health_check()
    logger.info(f"✅ Connected to API v{health['version']}")
except Exception as e:
    st.error(f"""
    **⚠️ Cannot connect to FastAPI backend**
    
    Please start the API server first:
    ```bash
    uvicorn api.main:app --reload
    ```
    
    Error: {str(e)}
    """)
    st.stop()

# ---- Header ----
st.markdown('<div class="main-header">📊 SkillLens Resume Analyzer</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-header">AI-powered skill analysis • Powered by FastAPI • v{APP_VERSION}</div>', unsafe_allow_html=True)

# ---- Main Upload Section ----
st.markdown("### 📄 Upload Resume")

col1, col2 = st.columns([2, 1])

with col1:
    uploaded_file = st.file_uploader(
        "Choose a PDF resume (max 5 MB)",
        type=["pdf"],
        help="Upload a text-based PDF resume for analysis"
    )

with col2:
    try:
        roles_response = api_client.get_roles()
        available_roles = roles_response["roles"]
    except Exception as e:
        logger.error(f"Failed to fetch roles: {e}")
        available_roles = ["Software Engineer"]
    
    target_role = st.selectbox(
        "🎯 Target Role",
        available_roles,
        help="Select the job role you're targeting"
    )

# ---- Analysis Button ----
if uploaded_file is not None:
    if st.button("🚀 Analyze Resume", type="primary", use_container_width=True):
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        try:
            with st.spinner("🔍 Analyzing your resume..."):
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
                
                # Update session state
                st.session_state.analysis_count += 1
                st.session_state.current_results = {
                    "skills": skills,
                    "found_skills": found_skills,
                    "missing_skills": missing_skills,
                    "coverage": coverage,
                    "target_role": target_role
                }
                
                st.success(f"✅ Analysis complete! Found {len(skills)} skills • {coverage:.1f}% match with {target_role}")
                
        except httpx.HTTPError as e:
            st.error(f"🌐 **API Error:** {str(e)}")
            logger.error(f"API call failed: {e}")
        except Exception as e:
            st.error(f"💥 **Error:** {str(e)}")
            logger.error(f"Analysis failed: {e}", exc_info=True)
        finally:
            # Clean up temp file
            Path(tmp_path).unlink(missing_ok=True)

# ---- Display Results ----
if st.session_state.current_results is not None:
    results = st.session_state.current_results
    
    st.markdown("---")
    st.markdown("## 📊 Analysis Results")
    
    # Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Coverage",
            value=f"{results['coverage']:.1f}%",
            delta=f"{results['coverage'] - 50:.1f}% vs avg" if results['coverage'] > 50 else None
        )
    
    with col2:
        st.metric(label="Total Skills", value=len(results['skills']))
    
    with col3:
        st.metric(label="Matched", value=len(results['found_skills']))
    
    with col4:
        st.metric(label="Missing", value=len(results['missing_skills']))
    
    # Skills Sections
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ✅ Your Skills")
        if results['skills']:
            skills_html = "".join([
                f'<span class="skill-tag">{skill}</span>'
                for skill in sorted(results['skills'])
            ])
            st.markdown(skills_html, unsafe_allow_html=True)
        else:
            st.info("No skills extracted")
    
    with col2:
        st.markdown(f"### 🎯 Skills for {results['target_role']}")
        if results['missing_skills']:
            st.markdown("**Missing Skills:**")
            missing_html = "".join([
                f'<span class="missing-skill-tag">{skill}</span>'
                for skill in sorted(results['missing_skills'][:10])
            ])
            st.markdown(missing_html, unsafe_allow_html=True)
        else:
            st.success("🎉 You have all the required skills!")
    
    # AI Insights Section
    st.markdown("---")
    st.markdown("## 🤖 AI Career Insights")
    
    ai_remaining = 5 - st.session_state.ai_insights_used
    
    if st.session_state.ai_insights_used >= 5:
        st.warning("⚠️ You've used all 5 AI insights for this session. Refresh the page to reset.")
    else:
        if st.button(f"✨ Get AI Recommendations ({ai_remaining}/5 remaining)", type="secondary"):
            try:
                with st.spinner("🧠 AI analyzing your profile..."):
                    ai_result = api_client.get_ai_insights(
                        found_skills=results['found_skills'],
                        missing_skills=results['missing_skills'],
                        target_role=results['target_role'],
                        coverage_percentage=results['coverage']
                    )
                
                if ai_result["success"]:
                    st.session_state.ai_recommendations = ai_result
                    st.session_state.ai_insights_used += 1
                    st.rerun()
                else:
                    st.error(f"❌ {ai_result.get('error', 'AI service unavailable')}")
                    
            except Exception as e:
                st.error(f"❌ AI insights failed: {str(e)}")
                logger.error(f"AI insights error: {e}")
    
    # Display AI Recommendations
    if st.session_state.ai_recommendations:
        recs = st.session_state.ai_recommendations
        
        # Create tabs for different insights
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Coverage Analysis",
            "🎯 Priority Skills",
            "📚 Learning Path",
            "💡 Projects",
            "✍️ Resume Tips"
        ])
        
        with tab1:
            st.markdown(recs['coverage_explanation'])
        
        with tab2:
            st.markdown(recs['top_missing_skills'])
        
        with tab3:
            st.markdown(recs['learning_path'])
        
        with tab4:
            st.markdown(recs['project_ideas'])
        
        with tab5:
            st.markdown(recs['resume_tweaks'])

# ---- Footer ----
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666; font-size: 0.9rem;'>
    Made with ❤️ by SkillLens • Analyses: {st.session_state.analysis_count} • 
    <a href='http://localhost:8000/docs' target='_blank'>API Docs</a>
</div>
""", unsafe_allow_html=True)
