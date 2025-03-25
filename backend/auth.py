import streamlit as st
import sqlite3
import bcrypt

def register_user(username, password):
    conn = sqlite3.connect("math_tutor.db")
    cursor = conn.cursor()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(username, password):
    conn = sqlite3.connect("math_tutor.db")
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    user_data = cursor.fetchone()
    conn.close()

    if user_data and bcrypt.checkpw(password.encode('utf-8'), user_data[0]):
        return True
    return False

def registration_page():
    st.subheader("🔐 Register")
    new_username = st.text_input("Username", key="reg_username")
    new_password = st.text_input("Password", type="password", key="reg_password")
    
    if st.button("Sign Up"):
        if new_username and new_password:
            if register_user(new_username, new_password):
                st.success("Registration successful! You can now log in.")
            else:
                st.error("Username already exists.")
        else:
            st.warning("Please fill in all fields.")

def login_page():
    st.subheader("🔑 Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login"):
        if login_user(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Welcome, {username}! 🎉")
            st.experimental_rerun()
        else:
            st.error("Invalid username or password.")
        st.rerun()  

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()
