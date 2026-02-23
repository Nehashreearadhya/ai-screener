# preprocessing/text_cleaner.py
import re

def clean_text_for_pdf(text):
    """
    Prepares text for PDF generation by removing characters 
    that cause FPDF to crash (emojis, complex symbols).
    """
    if not text:
        return ""
        
    # 1. Replace confusing characters (smart quotes, dashes)
    replacements = {
        u'\u201c': '"', u'\u201d': '"',  # Smart quotes
        u'\u2018': "'", u'\u2019': "'",  # Smart single quotes
        u'\u2013': '-', u'\u2014': '-',  # Dashes
        u'\u2022': '*',                  # Bullets
    }
    for search, replace in replacements.items():
        text = text.replace(search, replace)

    # 2. Encode to Latin-1 to strip emojis (replaces them with '?')
    # This prevents the "UnicodeEncodeError"
    return text.encode('latin-1', 'replace').decode('latin-1')

def clean_text_for_analysis(text):
    """
    Standard cleaning for AI analysis (removes extra whitespace).
    """
    if not text:
        return ""
    
    # Remove extra newlines and spaces
    text = re.sub(r'\s+', ' ', text)
    return text.strip()