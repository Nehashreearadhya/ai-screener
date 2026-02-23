import sys
import os
import re
from fpdf import FPDF
import tempfile

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from preprocessing.text_cleaner import clean_text_for_pdf
except ImportError:
    def clean_text_for_pdf(text):
        if not text: return ""
        return text.encode('latin-1', 'replace').decode('latin-1')

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.set_text_color(0, 51, 102)
        self.cell(0, 10, 'CareerVantage Analysis Report', 0, 1, 'C')
        self.ln(5)

    def section_title(self, title, color=(200, 220, 255)):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(*color)
        self.set_text_color(0, 0, 0)
        clean_title = clean_text_for_pdf(title)
        self.cell(0, 8, clean_title, 0, 1, 'L', 1)
        self.ln(3)

    def body_text(self, text, is_bold=False):
        self.set_font('Arial', 'B' if is_bold else '', 10)
        clean_text = clean_text_for_pdf(text)
        self.multi_cell(0, 5, clean_text)
        self.ln(1)

def create_pdf_report(name, ats_score, role, missing_skills, ai_feedback, resume_skills, required_skills):
    pdf = PDFReport()
    pdf.add_page()

    # --- 1. CANDIDATE PROFILE TABLE ---
    pdf.section_title("1. Candidate Profile")
    pdf.set_font('Arial', '', 10)
    
    # Table Header
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(50, 8, "Candidate Name", 1, 0, 'C', 1)
    pdf.cell(50, 8, "Target Role", 1, 0, 'C', 1)
    pdf.cell(40, 8, "ATS Score", 1, 0, 'C', 1)
    pdf.cell(50, 8, "Status", 1, 1, 'C', 1)
    
    # Table Data
    score_txt = f"{round(ats_score * 100, 1)}%"
    if ats_score >= 0.75: status = "Strong Match"
    elif ats_score >= 0.5: status = "Moderate Match"
    else: status = "Critical Gaps"
    
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(50, 10, clean_text_for_pdf(name), 1, 0, 'C')
    pdf.cell(50, 10, clean_text_for_pdf(role), 1, 0, 'C')
    pdf.cell(40, 10, score_txt, 1, 0, 'C')
    
    # Status Color Logic (Visual text only)
    if ats_score >= 0.5: pdf.set_text_color(0, 100, 0)
    else: pdf.set_text_color(200, 0, 0)
    pdf.cell(50, 10, status, 1, 1, 'C')
    pdf.set_text_color(0, 0, 0)
    pdf.ln(8)

    # --- 2. SKILL MATRIX ---
    pdf.section_title("2. Skill Analysis Matrix")
    pdf.set_font('Arial', 'B', 9)
    
    # Headers
    pdf.set_fill_color(230, 230, 250)
    pdf.cell(63, 8, "IDENTIFIED (Resume)", 1, 0, 'C', 1)
    pdf.cell(63, 8, "REQUIRED (JD)", 1, 0, 'C', 1)
    pdf.cell(63, 8, "MISSING (Gap)", 1, 1, 'C', 1)
    
    # Save Y position
    y_start = pdf.get_y()
    
    # Col 1
    pdf.set_xy(10, y_start)
    pdf.set_font('Arial', '', 8)
    pdf.set_text_color(0, 100, 0)
    txt1 = "\n".join([s.upper() for s in list(resume_skills)[:15]])
    pdf.multi_cell(63, 5, clean_text_for_pdf(txt1), border='LKB')
    y1 = pdf.get_y()
    
    # Col 2
    pdf.set_xy(73, y_start)
    pdf.set_text_color(0, 0, 128)
    txt2 = "\n".join([s.upper() for s in list(required_skills)[:15]])
    pdf.multi_cell(63, 5, clean_text_for_pdf(txt2), border='LKB')
    y2 = pdf.get_y()
    
    # Col 3
    pdf.set_xy(136, y_start)
    pdf.set_text_color(200, 0, 0)
    txt3 = "\n".join([s.upper() for s in list(missing_skills)[:15]]) if missing_skills else "None"
    pdf.multi_cell(63, 5, clean_text_for_pdf(txt3), border='LKB')
    y3 = pdf.get_y()
    
    pdf.set_xy(10, max(y1, y2, y3) + 5)
    pdf.set_text_color(0, 0, 0)

    # --- 3. STRATEGY ---
    pdf.section_title("3. Strategic Roadmap")
    if ai_feedback:
        # Clean Links
        clean_fb = re.sub(r"\[(.*?)\]\((.*?)\)", r"\1: \2", str(ai_feedback))
        lines = clean_fb.split('\n')
        for line in lines:
            line = line.strip()
            if not line: continue
            
            clean_line = clean_text_for_pdf(line)
            if "Recommended" in clean_line or "Internship" in clean_line or "Portfolio" in clean_line:
                pdf.ln(3)
                pdf.set_font('Arial', 'B', 11)
                pdf.set_fill_color(230, 230, 230)
                pdf.cell(0, 8, clean_line.replace('#', '').strip(), 0, 1, 'L', 1)
            elif clean_line.startswith(('1.', '2.', '3.')):
                pdf.ln(2)
                pdf.body_text(clean_line, is_bold=True)
            elif clean_line.startswith('-'):
                pdf.body_text("  " + clean_line)
            else:
                pdf.body_text(clean_line)
    
    pdf.ln(5)

    # --- 4. FORMATTING AUDIT (Table Format) ---
    pdf.section_title("4. Formatting Audit Checklist")
    pdf.set_font('Arial', '', 10)
    
    # Audit Table Header
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(50, 8, "Checklist Item", 1, 0, 'L', 1)
    pdf.cell(140, 8, "Action Required", 1, 1, 'L', 1)
    
    # Audit Table Body
    audit_items = [
        ("Contact Info", "Ensure email & phone are clearly visible at top."),
        ("Section Headers", "Use standard titles (Experience, Skills, Education)."),
        ("Bullet Points", "Start every bullet with a strong action verb."),
        ("File Format", "PDF is preferred over Word/Text."),
        ("Spelling", "Zero typos allowed. Use Grammarly/Spellcheck.")
    ]
    
    pdf.set_font('Arial', '', 10)
    for item, desc in audit_items:
        # Item Column
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(50, 8, item, 1)
        # Description Column
        pdf.set_font('Arial', '', 10)
        pdf.cell(140, 8, desc, 1, 1)

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    temp_file.close()
    pdf.output(temp_file.name)
    return temp_file.name