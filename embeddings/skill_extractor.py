# embeddings/skill_extractor.py

# Expanded list of skills
SKILLS = [
    # Programming Languages
    "python", "java", "c++", "javascript", "typescript", "html", "css", "sql", "nosql",
    
    # AI/ML
    "machine learning", "deep learning", "nlp", "computer vision", "tensorflow", "pytorch",
    "scikit-learn", "pandas", "numpy", "generative ai", "llm", "transformers",
    
    # Web & Frameworks
    "django", "flask", "fastapi", "react", "angular", "node.js", "spring boot",
    
    # DevOps & Cloud
    "aws", "azure", "google cloud", "docker", "kubernetes", "jenkins", "git", "linux"
]

def extract_skills(text):
    # This matches the skill if it appears anywhere in the lowercase text
    return [s for s in SKILLS if s in text.lower()]