# Description: A simple math tutor chatbot using the Gemini AI API to generate math questions and solutions.
import streamlit as st
import os
import sqlite3
from dotenv import load_dotenv
import google.generativeai as genai

# Load API Key
load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    st.error("API Key not found! Please check your .env file.")
models = genai.list_models()
# for model in models:
#     print(model.name)
# Initialize Gemini Models
query_refinement_model = genai.GenerativeModel("gemini-2.0-flash-lite")
question_generation_model = genai.GenerativeModel("gemini-2.0-flash-thinking-exp")

# Function to refine user input into structured query
def refine_query(user_input):
    prompt = f"""
    You are a math tutor's assistant. Given a raw user input, refine it into a clear and structured query.

    Example:
    User Input: "I want some algebra questions"
    Refined Query: "Generate 3 Algebra questions with solutions."

    User Input: "{user_input}"
    Refined Query:
    """
    response = query_refinement_model.generate_content(prompt)
    return response.text.strip() if response else "Unable to refine query."

# Function to get response from Gemini API
def get_gemini_response(prompt):
    try:
        chat = question_generation_model.start_chat(history=[])
        response = chat.send_message(prompt)
        return response.text.strip() if response else "No response from Gemini."
    except Exception as e:
        return f"Error: {str(e)}"

# Initialize SQLite database
def initialize_db():
    conn = sqlite3.connect("math_tutor.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT,
            difficulty TEXT,
            question TEXT,
            solution TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Function to save questions and solutions to the database
def save_questions_to_db(topic, questions, solutions):
    conn = sqlite3.connect("math_tutor.db")
    cursor = conn.cursor()
    
    difficulties = ["Basic", "Intermediate", "Advanced"]
    for idx, (question, solution) in enumerate(zip(questions, solutions)):
        cursor.execute("INSERT INTO questions (topic, difficulty, question, solution) VALUES (?, ?, ?, ?)", 
                       (topic, difficulties[idx % len(difficulties)], question, solution))
    
    conn.commit()
    conn.close()

# Function to fetch questions from the database
def fetch_questions_from_db(topic):
    conn = sqlite3.connect("math_tutor.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT question, solution FROM questions WHERE topic = ?", (topic,))
    rows = cursor.fetchall()
    
    conn.close()
    
    if not rows:
        return None, None
    
    questions, solutions = zip(*rows)
    return list(questions), list(solutions)

# Function to extract questions and solutions from Gemini API response
def extract_questions_and_solutions(response):
    """Extracts questions and solutions from Gemini response."""
    lines = response.split("\n")
    questions = []
    solutions = []
    current_question = None
    current_solution = None

    for line in lines:
        if line.strip().startswith("Q"):  # Identify questions
            if current_question and current_solution:
                questions.append(current_question)
                solutions.append(current_solution)
                current_solution = None
            current_question = line.strip()
        elif line.strip().startswith("A"):  # Identify solutions
            current_solution = line.strip()
    
    # Add last pair
    if current_question and current_solution:
        questions.append(current_question)
        solutions.append(current_solution)

    return questions[:3], solutions[:3]  # Ensure we return exactly 3

# Function to get questions (fetch from DB or generate via Gemini)
def get_questions(topic):
    questions, solutions = fetch_questions_from_db(topic)
    
    if not questions or not solutions:  # Generate if not found
        prompt = f"""
        Generate exactly 3 structured math questions for {topic}, each with a solution.
        Format:
        Q1: <question>
        A1: <solution>
        Q2: <question>
        A2: <solution>
        Q3: <question>
        A3: <solution>
        """
        response = get_gemini_response(prompt)

        if "Error" in response:
            st.error("Error while fetching questions from Gemini API.")
            return ["No question available"], ["No solution available"]

        questions, solutions = extract_questions_and_solutions(response)

        if len(questions) < 3 or len(solutions) < 3:
            st.error("Error: Gemini API returned an incomplete response.")
            return ["No question available"], ["No solution available"]
        
        save_questions_to_db(topic, questions, solutions)
    
    return questions, solutions

# Function to evaluate quiz and display score
def evaluate_quiz(answers, solutions):
    correct_count = 0
    total_questions = len(solutions)
    
    results = []
    for idx, (user_answer, correct_answer) in enumerate(zip(answers, solutions)):
        if user_answer.strip().lower() == correct_answer.strip().lower():
            correct_count += 1
            results.append(f"✅ Q{idx+1}: Correct!")
        else:
            results.append(f"❌ Q{idx+1}: Incorrect! Solution: {correct_answer}")

    score = f"**Your Score: {correct_count} / {total_questions}**"
    return score, results

# Initialize the database
initialize_db()

# Streamlit UI
st.set_page_config(page_title="Math Tutor Chatbot", layout="centered")
st.header("📚 Gemini Math Tutor 🤖")

# User input field for customized quiz
user_input = st.text_input("Enter your quiz request (e.g., 'Give me algebra questions'):")
# generate_quiz = st.button("Generate Quiz")

import streamlit as st

# Initialize session state variables
if "generate_quiz" not in st.session_state:
    st.session_state.generate_quiz = False
if "questions" not in st.session_state:
    st.session_state.questions = []
if "solutions" not in st.session_state:
    st.session_state.solutions = []
if "user_answers" not in st.session_state:
    st.session_state.user_answers = []
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False

# Button to start quiz
if st.button("Generate Quiz", key="generate_quiz_button"):
    st.session_state.generate_quiz = True
    st.session_state.quiz_submitted = False  # Reset submission state

if st.session_state.generate_quiz:
    user_input = st.text_input("Enter a math topic:")

    if user_input:
        refined_query = refine_query(user_input)
        st.write(f"🔍 **Refined Query:** {refined_query}")

        # Extract topic from refined query
        topic = None
        for t in ["Algebra", "Geometry", "Trigonometry"]:
            if t.lower() in refined_query.lower():
                topic = t
                break

        if topic:
            st.subheader(f"📝 Answer These {topic} Questions:")

            # Fetch questions only once
            if not st.session_state.questions or st.session_state.quiz_submitted:
                st.session_state.questions, st.session_state.solutions = get_questions(topic)
                st.session_state.user_answers = [""] * len(st.session_state.questions)
                st.session_state.quiz_submitted = False  # Reset submission state

            # Display questions and collect answers
            for idx, question in enumerate(st.session_state.questions):
                st.write(f"**Q{idx+1}:** {question}")
                st.session_state.user_answers[idx] = st.text_input(
                    f"Your answer to Q{idx+1}:",
                    key=f"answer_input_{idx}",
                    value=st.session_state.user_answers[idx]
                )

            # Ensure Submit button appears only once
            if not st.session_state.quiz_submitted:
                if st.button("Submit Answers", key="submit_quiz_button"):
                    score, results = evaluate_quiz(st.session_state.user_answers, st.session_state.solutions)
                    st.session_state.quiz_submitted = True  # Mark quiz as submitted

                    # Display results
                    st.subheader(score)
                    for result in results:
                        st.write(result)

        else:
            st.error("Sorry, I couldn't determine the topic. Please try again!")
