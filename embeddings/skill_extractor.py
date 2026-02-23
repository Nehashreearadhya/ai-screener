# embeddings/skill_extractor.py
import re

# --- 1. Expanded Skill Database (Tech + Non-Tech Roles) ---
SKILL_CATEGORIES = {
    # === TECHNOLOGY ROLES ===
    "Data Analyst": {
        "sql", "excel", "tableau", "power bi", "python", "r", "pandas", "numpy", 
        "data visualization", "statistics", "cleaning", "etl", "snowflake"
    },
    "Software Developer": {
        "python", "java", "c++", "c#", "javascript", "typescript", "react", "node.js", 
        "git", "docker", "agile", "sql", "dsa", "oop", "algorithms"
    },
    "Machine Learning Engineer": {
        "machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn", 
        "nlp", "computer vision", "transformers", "mlops", "aws sagemaker", "model deployment"
    },
    "DevOps Engineer": {
        "aws", "azure", "linux", "jenkins", "kubernetes", "docker", "terraform", 
        "ansible", "ci/cd", "bash", "scripting", "monitoring", "prometheus", "grafana"
    },
    "Cybersecurity Analyst": {
        "network security", "firewalls", "wireshark", "penetration testing", "siem", 
        "linux", "cryptography", "risk assessment", "incident response", "compliance", "kalilinux"
    },
    "Full Stack Developer": {
        "html", "css", "javascript", "react", "angular", "node.js", "django", "flask", 
        "mongodb", "sql", "rest api", "graphql", "aws", "git"
    },
    "Cloud Architect": {
        "aws", "azure", "gcp", "cloud formation", "iam", "vpc", "ec2", "s3", 
        "lambda", "microservices", "serverless", "distributed systems", "security"
    },
    "Network Engineer": {
        "tcp/ip", "dns", "dhcp", "vpn", "routing", "switching", "cisco", "juniper", 
        "firewalls", "lan", "wan", "subnetting", "wireshark"
    },
    "QA Automation Engineer": {
        "selenium", "junit", "testng", "pytest", "cypress", "appium", "java", "python", 
        "jenkins", "api testing", "postman", "jira", "agile"
    },
    "Product Manager": {
        "product roadmap", "agile", "scrum", "user stories", "market research", "jira", 
        "confluence", "stakeholder management", "analytics", "a/b testing", "ux"
    },
    "UI/UX Designer": {
        "figma", "adobe xd", "sketch", "wireframing", "prototyping", "user research", 
        "usability testing", "html", "css", "responsive design", "accessibility"
    },

    # === ACADEMIC & EDUCATION ROLES ===
    "School Teacher": {
        "classroom management", "lesson planning", "curriculum development", "student assessment",
        "special education", "differentiated instruction", "child psychology", "edtech", 
        "google classroom", "parent communication", "k-12", "literacy", "numeracy"
    },
    "PUC Lecturer": {
        "subject expertise", "lecturing", "student counseling", "examination duties", 
        "academic administration", "physics", "chemistry", "mathematics", "biology", 
        "college admissions", "competitive exam coaching", "lab supervision"
    },
    "Engineering Lecturer": {
        "teaching", "curriculum design", "research", "mentoring", "communication", 
        "matlab", "simulink", "autocad", "academic writing", "presentation", "pedagogy"
    },

    # === MEDICAL & SCIENCE ROLES ===
    "Doctor": {
        "patient care", "diagnosis", "surgery", "treatment planning", "medical records", 
        "emr", "clinical research", "public health", "emergency medicine", "pediatrics", 
        "internal medicine", "medical ethics", "hipaa", "cardiology", "anatomy"
    },
    "Scientist": {
        "hypothesis testing", "laboratory safety", "microscopy", "spectroscopy", 
        "chromatography", "pcr", "molecular biology", "chemistry", "physics", 
        "experimental design", "data analysis", "scientific writing", "peer review"
    },
    "Researcher": {
        "literature review", "data collection", "statistical analysis", "spss", "qualitative research", 
        "quantitative research", "grant writing", "publication", "surveys", "interviewing", 
        "critical thinking", "ethics"
    }
}

# Combine all unique skills into one set for general scanning
ALL_SKILLS = set().union(*SKILL_CATEGORIES.values())

def extract_skills(text):
    """Extracts all known skills from text using regex for accuracy."""
    text = text.lower()
    found_skills = set()
    
    # We check against the massive combined list of ALL skills
    for skill in ALL_SKILLS:
        # \b ensures exact word matching (e.g., avoids matching "java" in "javascript")
        if re.search(r"\b" + re.escape(skill) + r"\b", text):
            found_skills.add(skill)
            
    return found_skills

def detect_job_role(jd_text):
    """
    Auto-detects the job role by counting keywords and applying logic tweaks.
    """
    jd_text = jd_text.lower()
    role_scores = {}
    
    # 1. Base Score: Count how many skills from each category appear in the JD
    for role, skills in SKILL_CATEGORIES.items():
        count = sum(1 for skill in skills if skill in jd_text)
        role_scores[role] = count
    
    # 2. Context Boosting: Boost score if specific job titles appear in text
    if "school" in jd_text or "k-12" in jd_text or "grade" in jd_text:
        role_scores["School Teacher"] += 5
    elif "college" in jd_text or "university" in jd_text or "professor" in jd_text:
        role_scores["Engineering Lecturer"] += 3
        role_scores["PUC Lecturer"] += 3
    elif "hospital" in jd_text or "clinic" in jd_text or "patient" in jd_text:
        role_scores["Doctor"] += 5
    elif "lab" in jd_text or "experiment" in jd_text:
        role_scores["Scientist"] += 3
    
    # Return the role with the highest keyword match
    if not role_scores or max(role_scores.values()) == 0:
        return "Software Developer" # Default fallback
        
    return max(role_scores, key=role_scores.get)

def identify_missing_skills(resume_text, jd_text):
    # 1. Detect Role based on JD content
    role = detect_job_role(jd_text)
    
    # 2. Extract Skills
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)
    
    # 3. Find Missing Skills (only those present in JD but not in Resume)
    missing_skills = list(jd_skills - resume_skills)
    
    # 4. Calculate Weighted Score
    match_count = len(jd_skills.intersection(resume_skills))
    total_jd = len(jd_skills)
    
    keyword_score = match_count / total_jd if total_jd > 0 else 0
    
    return list(resume_skills), list(jd_skills), missing_skills, keyword_score, role