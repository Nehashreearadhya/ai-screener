from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer("all-MiniLM-L6-v2")
def similarity_score(resume_text, jd_text):
    emb1 = model.encode(resume_text, convert_to_tensor=True)
    emb2 = model.encode(jd_text, convert_to_tensor=True)
    return float(util.cos_sim(emb1, emb2))