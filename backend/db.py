import sqlite3

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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_questions_to_db(topic, questions, solutions):
    conn = sqlite3.connect("math_tutor.db")
    cursor = conn.cursor()
    
    difficulties = ["Basic", "Intermediate", "Advanced"]
    for idx, (question, solution) in enumerate(zip(questions, solutions)):
        cursor.execute("INSERT INTO questions (topic, difficulty, question, solution) VALUES (?, ?, ?, ?)", 
                       (topic, difficulties[idx % len(difficulties)], question, solution))
    
    conn.commit()
    conn.close()

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
