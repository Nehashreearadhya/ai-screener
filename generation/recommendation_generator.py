from transformers import pipeline
import random
import re

# Load distilgpt2 (Only used for unknown roles now)
try:
    generator = pipeline("text-generation", model="distilgpt2")
except Exception:
    generator = None

# --- 1. FULL SKILL DATABASE (For Context & Fallback) ---
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
        "linux", "cryptography", "risk assessment", "incident response", "compliance", "kali linux"
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

# --- 2. DIRECT COURSERA LINKS ---
RESOURCE_DB = {
    # Tech
    "python": "https://www.coursera.org/specializations/python",
    "sql": "https://www.coursera.org/learn/sql-for-data-science",
    "java": "https://www.coursera.org/specializations/java-programming",
    "react": "https://www.coursera.org/learn/react-basics",
    "machine learning": "https://www.coursera.org/specializations/machine-learning-introduction",
    "aws": "https://www.coursera.org/learn/aws-cloud-practitioner-essentials",
    "excel": "https://www.coursera.org/specializations/excel",
    "cybersecurity": "https://www.coursera.org/professional-certificates/google-cybersecurity",
    "data analysis": "https://www.coursera.org/professional-certificates/google-data-analytics",
    # Education
    "classroom management": "https://www.coursera.org/learn/teacher-relationships",
    "lesson planning": "https://www.coursera.org/learn/foundations-teaching-for-learning",
    # Medical
    "patient care": "https://www.coursera.org/learn/clinical-empathy",
    "public health": "https://www.coursera.org/specializations/public-health-perspectives",
    # General
    "project management": "https://www.coursera.org/professional-certificates/google-project-management",
    "communication": "https://www.coursera.org/specializations/effective-communication"
}

# --- 3. EXPANDED INTERNSHIP ADVICE ---
INTERNSHIP_DB = {
    # Tech
    "Data Analyst": "Look for 'Data Analytics Intern' roles at Fintech firms or 'Business Analyst' roles.",
    "Software Developer": "Apply for 'SDE Intern' roles or contribute to Open Source (Google Summer of Code).",
    "Machine Learning Engineer": "Seek 'AI Research Intern' roles or join Kaggle competitions.",
    "DevOps Engineer": "Look for 'Cloud Ops Intern' or 'Site Reliability Engineering (SRE) Intern' roles.",
    "Cybersecurity Analyst": "Apply for SOC Analyst internships or participate in Capture The Flag (CTF) events.",
    "Full Stack Developer": "Build a portfolio and apply to 'Web Development' internships at startups.",
    "Cloud Architect": "Get certified (AWS/Azure) and look for 'Cloud Support Associate' roles.",
    "Network Engineer": "Look for 'NOC Technician' or 'Network Support' internships.",
    "QA Automation Engineer": "Apply for 'Test Engineer Intern' roles; learn Selenium and JUnit.",
    "Product Manager": "Look for 'Associate Product Manager (APM)' rotational programs.",
    "UI/UX Designer": "Build a portfolio on Behance/Dribbble and apply for 'Product Design' internships.",
    
    # Education
    "School Teacher": "Apply for 'Student Teacher' placements or volunteer at local NGOs.",
    "PUC Lecturer": "Seek 'Guest Lecturer' spots or 'Teaching Assistant' roles in colleges.",
    "Engineering Lecturer": "Publish research papers and apply for 'Research Assistant' roles.",
    
    # Medical & Science
    "Doctor": "Look for 'Clinical Electives', 'Observerships', or 'Medical Scribe' roles.",
    "Scientist": "Apply for 'R&D Internships' in Pharma/Biotech or University Labs.",
    "Researcher": "Assist professors as a 'Research Assistant' or apply for grant-funded projects.",
    
    # Default
    "General": "Look for 'Summer Analyst' or 'Operations Intern' roles to gain corporate experience."
}

# --- 4. HARDCODED "JOB-WINNING" PROJECTS (For Every Role) ---
ROLE_PROJECTS = {
    # === TECHNOLOGY ===
    "Data Analyst": (
        "1. Beginner: Sales Dashboard - Create an interactive Excel/Tableau dashboard for retail sales.\n\n"
        "2. Intermediate: SQL Data Explorer - Build a Python tool to query and visualize a SQL database.\n\n"
        "3. Advanced: Customer Segmentation - Use Python and K-Means clustering to group customers."
    ),
    "Software Developer": (
        "1. Beginner: Task CLI - Build a command-line To-Do list manager in Python/Java.\n\n"
        "2. Intermediate: REST API Service - Create a backend API with Flask/Spring Boot and a database.\n\n"
        "3. Advanced: Real-time Chat App - Build a scalable chat system using WebSockets."
    ),
    "Machine Learning Engineer": (
        "1. Beginner: Iris Classifier - Train a simple model to classify flowers using Scikit-Learn.\n\n"
        "2. Intermediate: House Price Predictor - Build a regression model and deploy it via Streamlit.\n\n"
        "3. Advanced: Image Recognition App - Use TensorFlow/PyTorch to identify objects in photos."
    ),
    "DevOps Engineer": (
        "1. Beginner: Dockerized Web App - Containerize a simple static website using Docker.\n\n"
        "2. Intermediate: CI/CD Pipeline - Set up a GitHub Actions workflow to auto-deploy code to AWS.\n\n"
        "3. Advanced: Kubernetes Cluster - Deploy a microservices app on a k8s cluster with monitoring."
    ),
    "Cybersecurity Analyst": (
        "1. Beginner: Password Strength Checker - Python script to valid complexity of passwords.\n\n"
        "2. Intermediate: Network Scanner - Build a tool using Python Scapy to detect active devices.\n\n"
        "3. Advanced: Intrusion Detection System - Create a basic IDS to log suspicious network activity."
    ),
    "Full Stack Developer": (
        "1. Beginner: Personal Portfolio - Build a responsive website using React and CSS.\n\n"
        "2. Intermediate: E-Commerce Store - Create a shopping cart with Stripe payment integration.\n\n"
        "3. Advanced: Social Media Clone - Build a full-stack app with auth, posts, and comments."
    ),
    "Cloud Architect": (
        "1. Beginner: S3 Static Site - Host a website on AWS S3 with CloudFront CDN.\n\n"
        "2. Intermediate: Serverless API - Build an API using AWS Lambda and API Gateway.\n\n"
        "3. Advanced: 3-Tier Architecture - Design a scalable VPC network with private/public subnets."
    ),
    "Network Engineer": (
        "1. Beginner: Subnet Calculator - Build a Python tool to calculate IP ranges.\n\n"
        "2. Intermediate: Packet Sniffer - Use Wireshark/Python to capture and analyze local traffic.\n\n"
        "3. Advanced: Network Topology Sim - Design a corporate network using GNS3 or Cisco Packet Tracer."
    ),
    "QA Automation Engineer": (
        "1. Beginner: Bug Tracker - Create a simple spreadsheet or app to log software bugs.\n\n"
        "2. Intermediate: Selenium Bot - Write a script to automate login and form filling on a test site.\n\n"
        "3. Advanced: Test Framework - Build a hybrid framework using TestNG/JUnit with reporting."
    ),
    "Product Manager": (
        "1. Beginner: Product Teardown - Write a detailed critique of a popular app's UX/UI.\n\n"
        "2. Intermediate: Feature Spec - Write a PRD (Product Requirement Document) for a new feature.\n\n"
        "3. Advanced: MVP Launch - Build a no-code prototype using Bubble or Figma and test with users."
    ),
    "UI/UX Designer": (
        "1. Beginner: Icon Set - Design a cohesive set of 20 icons for a mobile app.\n\n"
        "2. Intermediate: App Redesign - Take a popular app and redesign its key user flows in Figma.\n\n"
        "3. Advanced: Design System - Create a comprehensive style guide and component library."
    ),

    # === ACADEMIC ===
    "School Teacher": (
        "1. Beginner: Lesson Plan Digitalizer - Create a template system for organizing weekly lessons.\n\n"
        "2. Intermediate: Student Progress Tracker - Simple Excel/App sheet to track grades over time.\n\n"
        "3. Advanced: Interactive Learning Game - Build a simple quiz game using Kahoot or PowerPoint macros."
    ),
    "PUC Lecturer": (
        "1. Beginner: Subject Blog - Start a blog explaining complex concepts in your field simply.\n\n"
        "2. Intermediate: Virtual Lab - Create a video series demonstrating key experiments/problems.\n\n"
        "3. Advanced: Exam Prep Guide - Compile a comprehensive study guide with solved past papers."
    ),
    "Engineering Lecturer": (
        "1. Beginner: Lab Manual - Write a detailed lab manual for a specific course module.\n\n"
        "2. Intermediate: Research Proposal - Draft a grant proposal for a specific engineering problem.\n\n"
        "3. Advanced: Simulation Model - Build a MATLAB/Simulink model to demonstrate a theoretical concept."
    ),

    # === MEDICAL & SCIENCE ===
    "Doctor": (
        "1. Beginner: Case Study Log - Maintain an anonymized log of interesting clinical cases.\n\n"
        "2. Intermediate: Public Health Pamphlet - Design an educational brochure for a common disease.\n\n"
        "3. Advanced: Clinical Audit - Conduct a review of patient outcomes to identify areas for improvement."
    ),
    "Scientist": (
        "1. Beginner: Lab Notebook - Maintain a digital, standardized lab notebook for experiments.\n\n"
        "2. Intermediate: Data Visualization - Use Python/R to create publication-quality plots of data.\n\n"
        "3. Advanced: Review Paper - Write a comprehensive literature review on a niche scientific topic."
    ),
    "Researcher": (
        "1. Beginner: Bibliography Manager - Organize citations using Zotero/Mendeley for a topic.\n\n"
        "2. Intermediate: Survey Analysis - Design, distribute, and analyze a survey using statistical tools.\n\n"
        "3. Advanced: Grant Application - Draft a full research grant application for a hypothetical study."
    ),

    # === FALLBACK ===
    "General": (
        "1. Beginner: Skill Tracker App - A simple tool to log daily learning progress.\n\n"
        "2. Intermediate: Data Dashboard - Visualizes real-time data from a public API.\n\n"
        "3. Advanced: Process Automation Bot - Script to automate a repetitive daily task."
    )
}

def generate_recommendations(missing_skills, role):
    # --- PART 1: COURSES ---
    resource_text = "### 📚 Recommended Coursera Certifications:\n"
    if missing_skills:
        for skill in missing_skills:
            link = RESOURCE_DB.get(skill.lower(), f"https://www.coursera.org/search?query={skill}")
            resource_text += f"- **{skill.upper()}**: [View Course]({link})\n"
    else:
        resource_text += "- **LEADERSHIP**: [View Course](https://www.coursera.org/specializations/organizational-leadership)\n"

    # --- PART 2: INTERNSHIPS ---
    internship_advice = INTERNSHIP_DB.get("General")
    # Fuzzy match role to Internship DB
    matched_intern_role = "General"
    for key in INTERNSHIP_DB:
        if key.lower() in role.lower():
            internship_advice = INTERNSHIP_DB[key]
            break
            
    internship_text = f"\n### 💼 Internship Recommendation:\n**Strategy:** {internship_advice}\n"

    # --- PART 3: PROJECTS (Hardcoded Lookup) ---
    # We bypass the AI generator to ensure 100% accurate, high-quality output
    # customized for the specific role.
    
    matched_role = "General"
    
    # Find best match in our ROLE_PROJECTS database
    # Priority: Exact match -> Fuzzy match -> General
    if role in ROLE_PROJECTS:
        matched_role = role
    else:
        for key in ROLE_PROJECTS:
            if key.lower() in role.lower():
                matched_role = key
                break
            
    strategy_text = ROLE_PROJECTS[matched_role]

    return f"{resource_text}{internship_text}\n###  Job Portfolio for {role}:\n{strategy_text}"