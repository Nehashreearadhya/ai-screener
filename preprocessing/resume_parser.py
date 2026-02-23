#resume_praser.py
from PyPDF2 import PdfReader
def extract_resume_text(path):
    reader = PdfReader(path)
    return "".join([p.extract_text() for p in reader.pages])