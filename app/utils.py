from fpdf import FPDF

def create_pdf_report(match_score, present_skills, missing_skills, feedback):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="AI Resume Screening Report", ln=True, align='C')
    pdf.ln(10)

    # Match Score
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=f"Match Score: {match_score:.2f}", ln=True)
    
    # Present Skills
    pdf.ln(5)
    pdf.cell(200, 10, txt="Present Skills:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, ", ".join(present_skills))

    # Missing Skills
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Missing Skills:", ln=True)
    pdf.set_font("Arial", size=12)
    # Check if there are missing skills to avoid empty strings
    if missing_skills:
        pdf.multi_cell(0, 10, ", ".join(missing_skills))
    else:
        pdf.multi_cell(0, 10, "None")

    # AI Feedback
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="AI Recommendations:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, feedback)

    return pdf.output(dest='S').encode('latin-1')