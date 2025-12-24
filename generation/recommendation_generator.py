from transformers import pipeline

# Load the AI model (this will download ~500MB the first time you run it)
generator = pipeline("text-generation", model="gpt2")

def generate_feedback(missing_skills):
    # If there are no missing skills, return a generic positive message
    if not missing_skills:
        return "Excellent! You have all the required skills."
        
    prompt = f"Suggest specific learning resources and projects to learn these technical skills: {', '.join(missing_skills)}"
    
    # Generate the response
    return generator(prompt, max_length=150, num_return_sequences=1)[0]['generated_text']