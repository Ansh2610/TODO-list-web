"""
SkillLens - Resume Analyzer v0.4.0
Milestone 4: Custom JD, PDF Preview, Learn Links, Export
"""
import os
import logging
import streamlit as st
import tempfile
import base64
import io
from pathlib import Path
import httpx
import json
from PIL import Image

from api.client import get_api_client
from backend.flags import (
    ENABLE_EXPORT_REPORT, 
    ENABLE_PDF_PREVIEW,
    MAX_AI_RUNS_PER_SESSION,
    MAX_ANALYSES_PER_SESSION
)

# ---- Configuration ----
APP_VERSION = "0.4.2"  # Fixed Streamlit Cloud deployment
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

# ---- Custom CSS ----
st.markdown("""
<style>
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
    .learn-link {
        display: inline-block;
        background: #F0F9FF;
        color: #0EA5E9;
        padding: 0.25rem 0.5rem;
        margin-left: 0.5rem;
        border-radius: 12px;
        font-size: 0.8rem;
        text-decoration: none;
        border: 1px solid #BAE6FD;
    }
    .learn-link:hover {
        background: #E0F2FE;
    }
    .pdf-preview-container {
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        overflow: hidden;
        height: 600px;
    }
    .privacy-footer {
        text-align: center;
        padding: 2rem 1rem;
        background: #F9FAFB;
        border-top: 1px solid #E5E7EB;
        margin-top: 3rem;
        border-radius: 8px;
    }
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

# ---- Load Learning Links (M4) ----
if st.session_state.learn_links_cache is None:
    try:
        response = api_client.get_learning_links_all()
        if response.get("success"):
            st.session_state.learn_links_cache = response.get("links", {})
            logger.info(f"✓ Loaded {len(st.session_state.learn_links_cache)} learning resources")
    except Exception as e:
        logger.warning(f"Failed to load learn links: {e}")
        st.session_state.learn_links_cache = {}

# ---- Header ----
st.markdown('<div class="main-header">📊 SkillLens Resume Analyzer</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-header">AI-powered skill analysis • Privacy-first • v{APP_VERSION}</div>', unsafe_allow_html=True)

# ---- Main Upload Section ----
st.markdown("### 📄 Upload Resume")

upload_col, role_col = st.columns([2, 1])

with upload_col:
    uploaded_file = st.file_uploader(
        "Choose a PDF resume (max 5 MB)",
        type=["pdf"],
        help="Upload a text-based PDF resume for analysis"
    )
    
    # Store PDF bytes for preview (M4)
    if uploaded_file is not None:
        st.session_state.uploaded_pdf_bytes = uploaded_file.getvalue()

with role_col:
    try:
        roles_response = api_client.get_roles()
        available_roles = roles_response["roles"]
    except Exception as e:
        logger.error(f"Failed to fetch roles: {e}")
        available_roles = ["Software Engineer"]
    
    # M4: Toggle between Role and Custom JD
    analysis_mode = st.radio(
        "Analysis Mode",
        ["📋 Role Template", "✍️ Custom JD"],
        horizontal=True
    )
    
    if analysis_mode == "📋 Role Template":
        st.session_state.use_custom_jd = False
        target_role = st.selectbox(
            "🎯 Target Role",
            available_roles,
            help="Select the job role you're targeting"
        )
        jd_text = None
    else:
        st.session_state.use_custom_jd = True
        target_role = None

# M4: Custom JD Input
if st.session_state.use_custom_jd:
    st.markdown("#### ✍️ Paste Job Description")
    jd_text = st.text_area(
        "Job Description Text",
        height=200,
        placeholder="Paste the full job description here (minimum 200 characters)...",
        help="Paste clean JD text including requirements, qualifications, and responsibilities"
    )
    
    if jd_text and len(jd_text.strip()) < 200:
        st.warning("⚠️ JD is too short. Please paste at least 200 characters of meaningful text.")

# ---- Analysis Button ----
if uploaded_file is not None:
    # Check session limits
    if st.session_state.analysis_count >= MAX_ANALYSES_PER_SESSION:
        st.warning(f"⚠️ You've reached the limit of {MAX_ANALYSES_PER_SESSION} analyses per session. Refresh to reset.")
    else:
        if st.button("🚀 Analyze Resume", type="primary", use_container_width=True):
            # Validate inputs
            if st.session_state.use_custom_jd and (not jd_text or len(jd_text.strip()) < 200):
                st.error("❌ Please paste a valid job description (at least 200 characters)")
                st.stop()
            
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
                    skills_by_category = parse_result.get("skills_by_category", {})
                    logger.info(f"✓ Parsed resume: {len(skills)} skills found")
                    
                    # Step 2: Benchmark via API (M4: supports JD text)
                    if st.session_state.use_custom_jd:
                        benchmark_result = api_client.benchmark_with_jd(
                            resume_skills=skills,
                            jd_text=jd_text
                        )
                        target_label = "Custom JD"
                    else:
                        benchmark_result = api_client.benchmark_skills(
                            resume_skills=skills,
                            target_role=target_role
                        )
                        target_label = target_role
                    
                    if not benchmark_result["success"]:
                        st.error(f"❌ {benchmark_result['error']}")
                        st.stop()
                    
                    coverage = benchmark_result["coverage_percentage"]
                    found_skills = benchmark_result["found_skills"]
                    missing_skills = benchmark_result["missing_skills"]
                    suggestions = benchmark_result.get("suggestions", {})
                    explanation = benchmark_result.get("explanation", "")
                    
                    # Update session state
                    st.session_state.analysis_count += 1
                    st.session_state.current_results = {
                        "skills": skills,
                        "skills_by_category": skills_by_category,
                        "found_skills": found_skills,
                        "missing_skills": missing_skills,
                        "coverage": coverage,
                        "coverage_percentage": coverage,  # Add this for consistency
                        "suggestions": suggestions,  # 🎯 THE FIX!
                        "explanation": explanation,  # 🎯 THE FIX!
                        "target_role": target_label,
                        "mode": "Custom JD" if st.session_state.use_custom_jd else "Role"
                    }
                    
                    st.success(f"✅ Analysis complete! Found {len(skills)} skills • {coverage:.1f}% match with {target_label}")
                    
            except httpx.HTTPError as e:
                st.error(f"🌐 **API Error:** {str(e)}")
                logger.error(f"API call failed: {e}")
            except Exception as e:
                st.error(f"💥 **Error:** {str(e)}")
                logger.error(f"Analysis failed: {e}", exc_info=True)
            finally:
                # Clean up temp file
                Path(tmp_path).unlink(missing_ok=True)

# ---- Display Results (M4: Two Column Layout with PDF Preview) ----
if st.session_state.current_results is not None:
    results = st.session_state.current_results
    
    st.markdown("---")
    
    # M4: Two-column layout (PDF Preview + Results)
    if ENABLE_PDF_PREVIEW and st.session_state.uploaded_pdf_bytes:
        pdf_col, results_col = st.columns([1, 1])
        
        with pdf_col:
            st.markdown("### 📄 Resume Preview")
            
            # Convert PDF to base64 for embedding
            base64_pdf = base64.b64encode(st.session_state.uploaded_pdf_bytes).decode('utf-8')
            
            # Use PDF.js with text layer for proper text selection and scrolling
            pdf_viewer_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    * {{
                        margin: 0;
                        padding: 0;
                        box-sizing: border-box;
                    }}
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                        background: #f5f5f5;
                        overflow: hidden;
                    }}
                    #pdf-viewer {{
                        width: 100%;
                        height: 100vh;
                        overflow-y: auto;
                        overflow-x: hidden;
                        background: #525659;
                        padding: 20px 10px;
                    }}
                    .pdf-page {{
                        position: relative;
                        margin: 0 auto 20px;
                        background: white;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
                        max-width: 100%;
                    }}
                    .pdf-page canvas {{
                        display: block;
                        width: 100%;
                        height: auto;
                    }}
                    .textLayer {{
                        position: absolute;
                        left: 0;
                        top: 0;
                        right: 0;
                        bottom: 0;
                        overflow: hidden;
                        opacity: 0.2;
                        line-height: 1.0;
                    }}
                    .textLayer > span {{
                        color: transparent;
                        position: absolute;
                        white-space: pre;
                        cursor: text;
                        transform-origin: 0% 0%;
                    }}
                    .textLayer ::selection {{
                        background: rgba(0, 100, 255, 0.4);
                    }}
                    .textLayer ::-moz-selection {{
                        background: rgba(0, 100, 255, 0.4);
                    }}
                    #loading {{
                        text-align: center;
                        padding: 40px;
                        color: white;
                        font-size: 16px;
                    }}
                    .page-number {{
                        text-align: center;
                        color: #666;
                        padding: 8px;
                        font-size: 12px;
                        background: #f9f9f9;
                        margin: 0 auto 10px;
                        width: fit-content;
                        border-radius: 4px;
                    }}
                </style>
            </head>
            <body>
                <div id="pdf-viewer">
                    <div id="loading">Loading PDF...</div>
                </div>
                
                <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
                <script>
                    pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
                    
                    // Convert base64 to Uint8Array
                    const pdfData = atob('{base64_pdf}');
                    const uint8Array = new Uint8Array(pdfData.length);
                    for (let i = 0; i < pdfData.length; i++) {{
                        uint8Array[i] = pdfData.charCodeAt(i);
                    }}
                    
                    const loadingTask = pdfjsLib.getDocument({{data: uint8Array}});
                    const viewer = document.getElementById('pdf-viewer');
                    
                    loadingTask.promise.then(async function(pdf) {{
                        viewer.innerHTML = '';
                        console.log('PDF loaded. Pages:', pdf.numPages);
                        
                        // Render all pages
                        for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {{
                            const page = await pdf.getPage(pageNum);
                            
                            // Create page container
                            const pageDiv = document.createElement('div');
                            pageDiv.className = 'pdf-page';
                            
                            // Add page number if multiple pages
                            if (pdf.numPages > 1) {{
                                const pageLabel = document.createElement('div');
                                pageLabel.className = 'page-number';
                                pageLabel.textContent = `Page ${{pageNum}} of ${{pdf.numPages}}`;
                                viewer.appendChild(pageLabel);
                            }}
                            
                            // Create canvas for rendering
                            const canvas = document.createElement('canvas');
                            const context = canvas.getContext('2d');
                            
                            // Calculate scale for good quality
                            const viewport = page.getViewport({{ scale: 1.5 }});
                            canvas.height = viewport.height;
                            canvas.width = viewport.width;
                            
                            pageDiv.appendChild(canvas);
                            
                            // Create text layer for text selection
                            const textLayerDiv = document.createElement('div');
                            textLayerDiv.className = 'textLayer';
                            textLayerDiv.style.width = viewport.width + 'px';
                            textLayerDiv.style.height = viewport.height + 'px';
                            pageDiv.appendChild(textLayerDiv);
                            
                            viewer.appendChild(pageDiv);
                            
                            // Render page canvas
                            await page.render({{
                                canvasContext: context,
                                viewport: viewport
                            }}).promise;
                            
                            // Render text layer for selection
                            const textContent = await page.getTextContent();
                            
                            textContent.items.forEach(function(textItem) {{
                                const tx = pdfjsLib.Util.transform(
                                    viewport.transform,
                                    textItem.transform
                                );
                                
                                const span = document.createElement('span');
                                span.textContent = textItem.str;
                                span.style.left = tx[4] + 'px';
                                span.style.top = (tx[5]) + 'px';
                                span.style.fontSize = (textItem.height) + 'px';
                                span.style.transform = `scaleX(${{textItem.width / (span.textContent.length * textItem.height * 0.5)}})`;
                                
                                textLayerDiv.appendChild(span);
                            }});
                        }}
                    }}).catch(function(error) {{
                        viewer.innerHTML = '<div id="loading">Error loading PDF: ' + error.message + '</div>';
                        console.error('Error:', error);
                    }});
                </script>
            </body>
            </html>
            """
            
            st.components.v1.html(pdf_viewer_html, height=760, scrolling=True)
            
            # Download button as backup
            st.download_button(
                label="📥 Download Resume",
                data=st.session_state.uploaded_pdf_bytes,
                file_name="resume.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
            # Show file info
            file_size_mb = len(st.session_state.uploaded_pdf_bytes) / (1024 * 1024)
            st.caption(f"📊 File size: {file_size_mb:.2f} MB")
            
        results_container = results_col
    else:
        results_container = st.container()
    
    with results_container:
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
        
        # Skills Display
        st.markdown("### ✅ Your Skills")
        if results['skills']:
            skills_html = "".join([
                f'<span class="skill-tag">{skill}</span>'
                for skill in sorted(results['skills'][:50])  # Limit display
            ])
            st.markdown(skills_html, unsafe_allow_html=True)
            if len(results['skills']) > 50:
                st.caption(f"... and {len(results['skills']) - 50} more")
        else:
            st.info("No skills extracted")
        
        # Missing Skills with Learn Links (M4)
        st.markdown(f"### 🎯 Missing Skills for {results['target_role']}")
        if results['missing_skills']:
            missing_with_links = ""
            for skill in sorted(results['missing_skills'][:15]):
                missing_with_links += f'<span class="missing-skill-tag">{skill}'
                
                # M4: Add learn link if available
                if skill in st.session_state.learn_links_cache:
                    link_data = st.session_state.learn_links_cache[skill]
                    missing_with_links += f'<a href="{link_data["url"]}" target="_blank" class="learn-link" title="{link_data["description"]}">Learn</a>'
                else:
                    # Fallback to Google search
                    google_url = f"https://www.google.com/search?q={skill.replace(' ', '+')}+tutorial"
                    missing_with_links += f'<a href="{google_url}" target="_blank" class="learn-link">Learn</a>'
                
                missing_with_links += '</span>'
            
            st.markdown(missing_with_links, unsafe_allow_html=True)
            if len(results['missing_skills']) > 15:
                st.caption(f"... and {len(results['missing_skills']) - 15} more missing skills")
        else:
            st.success("🎉 You have all the required skills!")
        
        # Explainable Match Feature (Killer Feature!)
        if results.get('suggestions') and len(results['suggestions']) > 0:
            st.markdown("---")
            st.markdown("### 💡 Smart Suggestions - Explainable Match")
            st.caption("See exactly how much each skill would boost your coverage!")
            
            # Sort suggestions by impact (highest boost first)
            sorted_suggestions = sorted(
                results['suggestions'].items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Display top 5 suggestions with % boost
            suggestions_html = ""
            for skill, boost in sorted_suggestions[:5]:
                new_coverage = results['coverage_percentage'] + boost
                suggestions_html += f'''
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                padding: 12px 16px; border-radius: 8px; margin-bottom: 8px;
                                box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="color: white; font-weight: 600; font-size: 15px;">
                                {skill}
                            </span>
                            <span style="background: rgba(255,255,255,0.2); color: white; 
                                         padding: 4px 12px; border-radius: 12px; font-size: 13px;">
                                +{boost}% → {new_coverage:.0f}%
                            </span>
                        </div>
                    </div>
                '''
            
            st.markdown(suggestions_html, unsafe_allow_html=True)
            
            if len(sorted_suggestions) > 5:
                st.caption(f"💡 Tip: Adding any of these {len(sorted_suggestions)} skills would boost your score!")
    
    # AI Insights Section
    st.markdown("---")
    st.markdown("## 🤖 AI Career Insights")
    
    ai_remaining = MAX_AI_RUNS_PER_SESSION - st.session_state.ai_insights_used
    
    if st.session_state.ai_insights_used >= MAX_AI_RUNS_PER_SESSION:
        st.warning(f"⚠️ You've used all {MAX_AI_RUNS_PER_SESSION} AI insights for this session. Refresh the page to reset.")
    else:
        if st.button(f"✨ Get AI Recommendations ({ai_remaining}/{MAX_AI_RUNS_PER_SESSION} remaining)", type="secondary"):
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
    
    # M4: Export Report
    if ENABLE_EXPORT_REPORT:
        st.markdown("---")
        st.markdown("### 📥 Export Report")
        
        export_col1, export_col2, export_col3 = st.columns(3)
        
        with export_col1:
            if st.button("📄 Download HTML", use_container_width=True):
                try:
                    response = api_client.export_report(
                        coverage_percent=results['coverage'],
                        missing_skills=results['missing_skills'],
                        skills_by_category=results.get('skills_by_category', {}),
                        target_role_label=results['target_role'],
                        mode=results.get('mode', 'Role'),
                        ai_recommendations=st.session_state.ai_recommendations if st.session_state.ai_recommendations else None,
                        format="html"
                    )
                    
                    if response.get('success'):
                        st.download_button(
                            label="💾 Save HTML Report",
                            data=response['content'],
                            file_name=response['filename'],
                            mime="text/html",
                            use_container_width=True
                        )
                    else:
                        st.error(f"Failed: {response.get('error', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Export failed: {e}")
        
        with export_col2:
            if st.button("📋 Download JSON", use_container_width=True):
                try:
                    response = api_client.export_report(
                        coverage_percent=results['coverage'],
                        missing_skills=results['missing_skills'],
                        skills_by_category=results.get('skills_by_category', {}),
                        target_role_label=results['target_role'],
                        mode=results.get('mode', 'Role'),
                        ai_recommendations=st.session_state.ai_recommendations if st.session_state.ai_recommendations else None,
                        format="json"
                    )
                    
                    if response.get('success'):
                        st.download_button(
                            label="💾 Save JSON Report",
                            data=response['content'],
                            file_name=response['filename'],
                            mime="application/json",
                            use_container_width=True
                        )
                    else:
                        st.error(f"Failed: {response.get('error', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Export failed: {e}")
        
        with export_col3:
            if st.button("📝 Download Text", use_container_width=True):
                try:
                    response = api_client.export_report(
                        coverage_percent=results['coverage'],
                        missing_skills=results['missing_skills'],
                        skills_by_category=results.get('skills_by_category', {}),
                        target_role_label=results['target_role'],
                        mode=results.get('mode', 'Role'),
                        ai_recommendations=st.session_state.ai_recommendations if st.session_state.ai_recommendations else None,
                        format="text"
                    )
                    
                    if response.get('success'):
                        st.download_button(
                            label="💾 Save Text Report",
                            data=response['content'],
                            file_name=response['filename'],
                            mime="text/plain",
                            use_container_width=True
                        )
                    else:
                        st.error(f"Failed: {response.get('error', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Export failed: {e}")

# ---- M4: Privacy Footer ----
st.markdown("---")
st.markdown(f"""
<div class="privacy-footer">
    <h4>🔒 Privacy-First Analysis</h4>
    <p style="color: #6B7280; font-size: 0.95rem; max-width: 800px; margin: 1rem auto;">
        <strong>Your resume is never stored.</strong> We only extract skill names for comparison. 
        No raw text is sent to AI services. All processing happens locally and is deleted immediately after analysis.
    </p>
    <p style="color: #9CA3AF; font-size: 0.85rem; margin-top: 1rem;">
        © 2025 SkillLens v{APP_VERSION} • Analyses: {st.session_state.analysis_count} • 
        <a href="{API_BASE_URL}/docs" target="_blank" style="color: #6366F1;">API Docs</a>
    </p>
</div>
""", unsafe_allow_html=True)
