import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load API Key
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    raise ValueError("API Key not found! Check your .env file.")

query_refinement_model = genai.GenerativeModel("gemini-2.0-flash-lite")
question_generation_model = genai.GenerativeModel("gemini-2.0-flash-thinking-exp")

def refine_query(user_input):
    prompt = f"""
    You are a math tutor's assistant. Given a raw user input, refine it into a structured query.

    Example:
    User Input: "I want some algebra questions"
    Refined Query: "Generate 3 Algebra questions with solutions."

    User Input: "{user_input}"
    Refined Query:
    """
    response = query_refinement_model.generate_content(prompt)
    return response.text.strip() if response else "Unable to refine query."

def get_gemini_response(prompt):
    try:
        chat = question_generation_model.start_chat(history=[])
        response = chat.send_message(prompt)
        return response.text.strip() if response else "No response from Gemini."
    except Exception as e:
        return f"Error: {str(e)}"
