import streamlit as st
from db import fetch_questions_from_db, save_questions_to_db
from gemini_api import get_gemini_response, refine_query

def extract_questions_and_solutions(response):
    lines = response.split("\n")
    questions, solutions = [], []
    current_question, current_solution = None, None

    for line in lines:
        if line.strip().startswith("Q"):
            if current_question and current_solution:
                questions.append(current_question)
                solutions.append(current_solution)
            current_question = line.strip()
        elif line.strip().startswith("A"):
            current_solution = line.strip()

    if current_question and current_solution:
        questions.append(current_question)
        solutions.append(current_solution)

    return questions[:3], solutions[:3]

def get_questions(topic):
    questions, solutions = fetch_questions_from_db(topic)
    if not questions or not solutions:
        prompt = f"Generate 3 {topic} questions with solutions in Q&A format."
        response = get_gemini_response(prompt)

        if "Error" in response:
            return ["No question available"], ["No solution available"]

        questions, solutions = extract_questions_and_solutions(response)
        save_questions_to_db(topic, questions, solutions)
    
    return questions, solutions

def quiz_page():
    user_input = st.text_input("Enter a math topic:")
    if st.button("Generate Quiz"):
        refined_query = refine_query(user_input)
        topic = refined_query.split(" ")[-2]  # Extract topic from refined query
        st.subheader(f"📝 {topic} Quiz")
        
        questions, solutions = get_questions(topic)
        for idx, question in enumerate(questions):
            st.text_input(question, key=f"answer_{idx}")
