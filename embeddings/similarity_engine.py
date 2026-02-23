import re
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_ats_score(resume_text, jd_text, kw_match_score):
    """
    Calculates a weighted ATS score using a hybrid of:
    1. Exact Keyword Matching (High Precision)
    2. Cosine Similarity (Context/Semantics)
    3. Boosting Curve (To normalize scores for realistic JDs)
    """
    
    # --- 1. Semantic Match (Context) ---
    # This helps if you have the *experience* but used slightly different words
    try:
        text_list = [resume_text, jd_text]
        cv = CountVectorizer(stop_words='english')
        count_matrix = cv.fit_transform(text_list)
        semantic_score = cosine_similarity(count_matrix)[0][1]
    except Exception:
        semantic_score = 0.0

    # --- 2. Weighted Hybrid Calculation ---
    # Keywords are King in ATS, so we give them 70% weight.
    # Semantic context gets 30%.
    raw_score = (kw_match_score * 0.7) + (semantic_score * 0.3)

    # --- 3. The "Reality Curve" (Boosting) ---
    # Most JDs list 50+ skills. Matching 25% of them is actually a GOOD score.
    # We apply a 2x multiplier to normalize the score to a human-readable scale.
    # Example: 
    #   Raw Match 20% -> Boosted to 40% (Moderate)
    #   Raw Match 30% -> Boosted to 60% (Strong)
    
    boosted_score = raw_score * 2.5 # Multiplier to lift the range
    
    # Apply Limits (Cap at 98%, Floor at 10%)
    final_score = min(0.98, max(0.10, boosted_score))

    return final_score