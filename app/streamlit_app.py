import streamlit as st
import sys
import os

# Ensure the root folder is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import custom modules
try:
    from preprocessing.resume_parser import extract_resume_text
    from preprocessing.jd_parser import extract_jd_text
    from embeddings.skill_extractor import identify_missing_skills
    from embeddings.similarity_engine import calculate_ats_score
    from generation.recommendation_generator import generate_recommendations
    from app.utils import create_pdf_report
except ImportError as e:
    st.error(f"Import Error: {e}. Please check your folder structure and file names.")
    st.stop()

# --- Page Configuration ---
st.set_page_config(
    page_title="CareerVantage",
    page_icon="🚀",
    layout="wide"
)

# --- Custom CSS for Professional UI ---
st.markdown("""
<style>
    /* 1. Global Font Styles */
    html, body, [class*="css"] {
        font-family: 'Roboto', 'Helvetica', 'Arial', sans-serif;
        background-color: #f5f7fa;
    }

    /* 2. Hero Section */
    .hero {
        background: linear-gradient(135deg, #004B8D 0%, #0074D9 100%);
        padding: 40px 20px;
        text-align: center;
        border-radius: 0 0 20px 20px;
        margin-bottom: 30px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .hero h1 {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 10px;
        color: white !important;
    }
    .hero h3 {
        font-size: 1.5rem;
        font-weight: 300;
        margin-top: 0;
        color: #E0E0E0 !important;
    }

    /* 3. Input Cards */
    .stTextInput, .stTextArea, .stFileUploader {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #e1e4e8;
    }

    /* 4. Primary Button */
    .stButton>button {
        background: linear-gradient(90deg, #00C853 0%, #009624 100%);
        color: white;
        font-size: 20px;
        padding: 12px 45px;
        border-radius: 50px;
        border: none;
        box-shadow: 0 4px 15px rgba(0, 200, 83, 0.3);
        font-weight: bold;
        transition: all 0.3s ease;
        display: block;
        margin: 0 auto;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 200, 83, 0.4);
    }

    /* 5. Metrics & Skills */
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        color: #004B8D;
    }
    
    /* Skill Pills Styling */
    .skill-pill-green {
        background-color: #e8f5e9;
        color: #2e7d32;
        padding: 6px 14px;
        border-radius: 20px;
        margin: 4px;
        font-weight: 600;
        display: inline-block;
        border: 1px solid #a5d6a7;
    }
    .skill-pill-blue {
        background-color: #e3f2fd;
        color: #1565c0;
        padding: 6px 14px;
        border-radius: 20px;
        margin: 4px;
        font-weight: 600;
        display: inline-block;
        border: 1px solid #90caf9;
    }
    .skill-pill-red {
        background-color: #ffebee;
        color: #c62828;
        padding: 6px 14px;
        border-radius: 20px;
        margin: 4px;
        font-weight: 600;
        display: inline-block;
        border: 1px solid #ef9a9a;
    }
</style>
""", unsafe_allow_html=True)

# --- Hero Section ---
st.markdown("""
<div class="hero">
    <h1>CareerVantage</h1>
    <h3>Analyze. Optimize. Get Hired.</h3>
</div>
""", unsafe_allow_html=True)

# --- Input Section ---
st.markdown("### 👤 Candidate Details")
name_input = st.text_input("Enter your full name", placeholder="e.g. Alex Smith", label_visibility="collapsed")
st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1], gap="large")
with col1:
    st.markdown("### 📄 Upload Resume")
    resume_file = st.file_uploader("Upload your PDF resume", type=["pdf"], label_visibility="collapsed")
with col2:
    st.markdown("### 💼 Job Description")
    jd_input = st.text_area("Paste JD text here", height=150, placeholder="Paste the job description...", label_visibility="collapsed")

st.markdown("<br>", unsafe_allow_html=True)

# Analyze Button
col_spacer1, col_btn, col_spacer2 = st.columns([1, 2, 1])
with col_btn:
    analyze_btn = st.button("🚀 Analyze My Fit", use_container_width=True)

# --- Logic ---
if analyze_btn:
    final_name = name_input if name_input.strip() else "Candidate"
    
    if resume_file and jd_input:
        ats_score = 0.0
        role = "General"
        missing = []
        ai_advice = ""
        resume_skills = set()
        required_skills = set()

        with st.spinner(f"Running AI Analysis for {final_name}..."):
            try:
                # 1. Parsing
                resume_text = extract_resume_text(resume_file)
                jd_text = extract_jd_text(jd_input)

                if not resume_text.strip():
                    st.error("Error: The Resume PDF appears empty.")
                    st.stop()

                # 2. Skill Extraction & Scoring
                resume_skills, required_skills, missing, kw_score, role = identify_missing_skills(resume_text, jd_text)
                raw_ats_score = calculate_ats_score(resume_text, jd_text, kw_score)
                ats_score = max(0.0, min(float(raw_ats_score), 1.0))
                
                # 3. AI Recommendations
                ai_advice = generate_recommendations(missing, role)
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.stop()

        # --- RESULTS DISPLAY ---
        st.markdown("---")
        st.success(f"✅ Analysis Complete for **{final_name}**")
        st.info(f"🎯 Target Role Detected: **{role}**")
        
        # 1. METRICS ROW
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("ATS Score", f"{round(ats_score*100, 1)}%")
            if ats_score < 0.5:
                st.error("Low Match")
            elif ats_score < 0.75:
                st.warning("Moderate Match")
            else:
                st.success("Strong Match")
        
        with m2:
            st.metric("Skills Found", len(resume_skills))
        with m3:
            st.metric("Missing Skills", len(missing))

        st.markdown("---")
        
        # 2. 3-COLUMN SKILL MATRIX
        st.markdown("### 🧬 Detailed Skill Analysis")
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.markdown("#### ✅ Identified Skills (Resume)")
            if resume_skills:
                html = "".join([f"<span class='skill-pill-green'>{s.upper()}</span>" for s in resume_skills])
                st.markdown(html, unsafe_allow_html=True)
            else:
                st.markdown("*No skills found.*")

        with c2:
            st.markdown("#### 🔹 Required Skills (JD)")
            if required_skills:
                html = "".join([f"<span class='skill-pill-blue'>{s.upper()}</span>" for s in required_skills])
                st.markdown(html, unsafe_allow_html=True)
            else:
                st.markdown("*No requirements found.*")

        with c3:
            st.markdown("#### ⚠️ Missing Skills (Gap)")
            if missing:
                html = "".join([f"<span class='skill-pill-red'>{s.upper()}</span>" for s in missing])
                st.markdown(html, unsafe_allow_html=True)
                if ats_score < 0.1:
                    st.error("🚨 Critical Gaps Detected!")
            else:
                st.success("✅ No Missing Skills!")

        # 3. AI STRATEGY
        st.markdown("---")
        st.subheader("💡 AI Improvement Strategy")
        st.markdown(ai_advice)
        
        # 4. PDF REPORT
        # Make sure your create_pdf_report function in app/utils.py accepts these new arguments
        pdf_path = create_pdf_report(final_name, ats_score, role, missing, ai_advice, resume_skills, required_skills)
        
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
            
        st.download_button(
            label="📥 Download Professional Report (PDF)",
            data=pdf_bytes,
            file_name=f"{final_name.replace(' ', '_')}_CareerVantage_Report.pdf",
            mime="application/pdf"
        )

    else:
        st.warning("⚠️ Please upload both a Resume and a Job Description to start.")