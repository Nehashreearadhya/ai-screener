import sys
import os


# Get the absolute path to the main 'ai-resume-screening' folder
# This moves two levels up: from streamlit_app.py -> app -> ai-resume-screening
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- The rest of your imports go here ---
import streamlit as st
from preprocessing.resume_parser import extract_resume_text
from preprocessing.jd_parser import extract_jd_text
from embeddings.skill_extractor import extract_skills
from embeddings.similarity_engine import similarity_score
from generation.recommendation_generator import generate_feedback
from app.utils import create_pdf_report

# ... The rest of your application code ...

# --- Input Section ---
resume = st.file_uploader("Upload Resume (PDF)")
jd_input = st.text_area("Paste Job Description")

if resume and jd_input:
    # 1. Process Text
    resume_text = extract_resume_text(resume)
    jd_text = extract_jd_text(jd_input)
    
    # 2. Extract Skills from BOTH
    resume_skills = set(extract_skills(resume_text))
    jd_skills = set(extract_skills(jd_text))
    
    # 3. Calculate Missing Skills (Gap Analysis)
    missing_skills = jd_skills - resume_skills
    
    # 4. Calculate Similarity Score
    match_score = similarity_score(resume_text, jd_text)
    
    # --- Display Results ---
    st.header("Analysis Results")
    
    # Display Score
    st.metric(label="Match Score", value=f"{match_score:.2f}")
    
    # Display Skills in Columns
    col1, col2 = st.columns(2)
    with col1:
        st.write("✅ **Present Skills:**", list(resume_skills))
    with col2:
        st.write("⚠️ **Missing Skills:**", list(missing_skills))
    
    # --- AI Feedback & PDF Preparation ---
    feedback_text = ""  # Initialize variable to store feedback for the PDF
    
    if missing_skills:
        st.subheader("AI Improvement Recommendations")
        # Generate feedback and store it
        feedback_text = generate_feedback(list(missing_skills))
        st.write(feedback_text)
    else:
        st.success("Great match! No critical skills missing from the predefined list.")
        feedback_text = "Great match! Keep up the good work."

    # --- Export to PDF ---
    st.markdown("---")  # Visual separator
    
    # Generate the PDF binary data
    pdf_data = create_pdf_report(
        match_score, 
        list(resume_skills), 
        list(missing_skills), 
        feedback_text
    )
    
    # Download Button
    st.download_button(
        label="📄 Download Report as PDF",
        data=pdf_data,
        file_name="resume_analysis_report.pdf",
        mime="application/pdf"
    )