"""
SkillLens MVP - Streamlit Application
Secure resume analysis with PDF parsing, skill extraction, and role coverage visualization
"""
import os
import json
import logging
import streamlit as st
from dotenv import load_dotenv

from backend.security import allowed_file, validate_file_size, secure_hash_name
from backend.parser import extract_text_from_pdf
from backend.utils import load_json, load_stopwords
from backend.skills import extract_skills, flatten_categories, coverage_against_role
from backend.viz import bar_coverage_chart, radar_skill_categories

# ---- Constants ----
APP_VERSION = "0.1.0"
ACCENT_COLOR = "#6366F1"  # Indigo

# ---- Logging Configuration ----
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ---- Bootstrap ----
load_dotenv()
st.set_page_config(
    page_title="SkillLens — Resume Analyzer",
    layout="centered",
    page_icon="🎯",
    initial_sidebar_state="collapsed"
)

# ---- Soft rate-limit per session ----
if "analysis_count" not in st.session_state:
    st.session_state.analysis_count = 0

# ---- Cache data ----
@st.cache_data
def _load_roles():
    return load_json("data/roles.json")

@st.cache_data
def _load_skill_bank():
    return load_json("data/skill_bank.json")

@st.cache_data
def _load_stopwords():
    return load_stopwords("data/stopwords.txt")

roles = _load_roles()
skill_bank = _load_skill_bank()
stopwords = _load_stopwords()

# ---- UI ----
st.markdown("""
    <h1 style='font-size: 24px; font-weight: bold; margin-bottom: 0.5rem;'>
        SkillLens — Resume Analyzer (MVP)
    </h1>
    """, unsafe_allow_html=True)
st.caption("Local resume → skill extraction → role coverage. No data stored.")

with st.expander("🔒 Security & Privacy Policy", expanded=False):
    st.markdown("""
### Enforced Security Limits
- **PDF only**, max 5 MB (strict MIME type validation)
- **Text-only extraction** (no embedded code execution)
- **Text truncation** at 100,000 characters for privacy and performance
- **No resume text saved to disk**; session-only processing
- **Minimal logs**; no personally identifiable information (PII) stored
- **Session limited to 10 analyses** to prevent abuse
- **All processing happens locally** in your browser session

### Edge Cases Tested
✓ Non-PDF files rejected  
✓ Files >5 MB rejected  
✓ Scanned/image-only PDFs handled gracefully  
✓ Role switching works correctly  
✓ Rate limit enforced after 10 analyses  
""")

col1, col2 = st.columns([2, 1])
with col1:
    uploaded = st.file_uploader("Upload your resume (PDF only, ≤ 5 MB)", type=["pdf"])
with col2:
    target_role = st.selectbox("Target Role", options=list(roles.keys()))

# Show role template preview
with st.expander(f"📋 View {target_role} skills template", expanded=False):
    role_skills_preview = roles.get(target_role, [])
    st.write(f"**Required skills ({len(role_skills_preview)})**: " + ", ".join(role_skills_preview))

analyze_disabled = uploaded is None or st.session_state.analysis_count >= 10
analyze = st.button(
    "Analyze Resume",
    type="primary",
    disabled=analyze_disabled,
    use_container_width=True
)

# ---- Action ----
if analyze:
    if st.session_state.analysis_count >= 10:
        st.error("⚠️ Session analysis limit reached (10). Please refresh the page or restart the app to continue.")
        st.stop()

    if uploaded is None:
        st.warning("⚠️ Please upload a PDF file to analyze.")
        st.stop()

    # Validate file
    mime = uploaded.type
    fname = uploaded.name
    data = uploaded.read()

    # Check file type
    if not allowed_file(fname, mime):
        st.error("❌ Invalid file type. Only PDF files are accepted. Please upload a PDF resume.")
        logger.warning(f"Invalid file type rejected: {fname} (MIME: {mime})")
        st.stop()
    
    # Check file size
    if not validate_file_size(data):
        st.error(f"❌ File too large ({len(data) / (1024*1024):.1f} MB). Please upload a file ≤ 5 MB.")
        logger.warning(f"File too large rejected: {fname} ({len(data)} bytes)")
        st.stop()

    safe_name = secure_hash_name(fname)
    logger.info(f"Analysis started | file={fname} | size={len(data)} bytes")

    # Extract text
    with st.spinner("Extracting text from PDF..."):
        try:
            text = extract_text_from_pdf(data)
        except Exception as e:
            st.error(f"❌ Failed to parse PDF: {str(e)}. Please ensure the file is not corrupted or password-protected.")
            logger.error(f"PDF parsing failed: {fname} - {str(e)}")
            st.stop()

    # Basic metrics
    char_count = len(text or "")
    word_count = len((text or "").split())
    
    # Check if text was truncated
    from backend.security import MAX_TEXT_CHARS
    was_truncated = char_count >= MAX_TEXT_CHARS
    
    if char_count == 0:
        st.error("❌ No text could be extracted from this PDF. Please ensure it's a text-based PDF (not a scanned image).")
        logger.warning(f"No text extracted from: {fname}")
        st.stop()
    
    st.success("✅ Text extracted successfully.")
    if was_truncated:
        st.info(f"ℹ️ Large file truncated to {MAX_TEXT_CHARS:,} characters for privacy and performance.")
    st.write(f"**Characters**: {char_count:,}  |  **Words**: {word_count:,}")

    # Extract skills
    with st.spinner("Analyzing skills and matching to role..."):
        extracted = extract_skills(text, skill_bank)
        flat = flatten_categories(extracted)

    # Coverage vs selected role
    role_skills = roles.get(target_role, [])
    coverage, missing = coverage_against_role(flat, role_skills)
    
    logger.info(f"Analysis completed | chars={char_count} | coverage={coverage}% | skills_found={len(flat)}")

    st.divider()
    st.markdown(f"<h2 style='font-size: 20px; font-weight: 600; margin: 1rem 0;'>📊 Results</h2>", unsafe_allow_html=True)
    st.markdown(f"Your resume currently matches **{coverage}%** of core **{target_role}** skills.")
    st.caption(f"Detected **{len(flat)} unique skills** across {len([c for c in extracted.values() if c])} categories")

    # Visuals
    col_a, col_b = st.columns(2)
    with col_a:
        st.plotly_chart(bar_coverage_chart(coverage, ACCENT_COLOR), use_container_width=True)
    with col_b:
        st.plotly_chart(radar_skill_categories(extracted, ACCENT_COLOR), use_container_width=True)

    st.markdown(f"<h2 style='font-size: 20px; font-weight: 600; margin: 1rem 0;'>🎯 Extracted Skills by Category</h2>", unsafe_allow_html=True)
    for cat, items in extracted.items():
        if items:
            st.write(f"**{cat.replace('_', ' ').title()}**: " + ", ".join(sorted(items)))
        else:
            st.write(f"**{cat.replace('_', ' ').title()}**: _(none detected)_")

    st.markdown(f"<h2 style='font-size: 20px; font-weight: 600; margin: 1rem 0;'>⚠️ Missing vs Role Template</h2>", unsafe_allow_html=True)
    if missing:
        st.write(", ".join(sorted(missing)))
        st.caption(f"{len(missing)} skill(s) from the {target_role} template not found in your resume")
    else:
        st.success("✅ No gaps found against the MVP template (excellent match!).")

    # Download JSON
    result = {
        "target_role": target_role,
        "coverage": coverage,
        "missing_skills": missing,
        "extracted_by_category": extracted,
        "extracted_flat_unique": flat,
        "analysis_metadata": {
            "character_count": char_count,
            "word_count": word_count,
            "truncated": was_truncated,
            "app_version": APP_VERSION
        }
    }
    
    # JSON Preview
    with st.expander("📄 Preview JSON results", expanded=False):
        st.json(result)
    
    st.download_button(
        "📥 Download JSON",
        data=json.dumps(result, indent=2),
        file_name=f"skilllens_{safe_name}.json",
        mime="application/json",
        use_container_width=True
    )

    # Increment session count
    st.session_state.analysis_count += 1
    st.caption(f"_Session analyses used: {st.session_state.analysis_count}/10_")

# Footer
st.divider()
st.markdown(f"""
<div style='text-align: center; color: #6B7280; font-size: 14px; padding: 1rem 0;'>
    © SkillLens v{APP_VERSION} | No data stored | 
    <a href='https://github.com/Ansh2610/TODO-list-web' target='_blank' style='color: {ACCENT_COLOR}; text-decoration: none;'>
        View Source on GitHub 🔗
    </a>
</div>
""", unsafe_allow_html=True)
