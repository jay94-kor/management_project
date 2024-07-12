import hashlib
import streamlit as st
import sqlite3

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate(username, password):
    conn = sqlite3.connect('budget_management.db')
    c = conn.cursor()
    hashed_password = hash_password(password)
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, hashed_password))
    user = c.fetchone()
    conn.close()
    return user

def login():
    st.sidebar.title("로그인")
    username = st.sidebar.text_input("사용자 이름")
    password = st.sidebar.text_input("비밀번호", type='password')
    if st.sidebar.button("로그인"):
        user = authenticate(username, password)
        if user:
            st.session_state['logged_in'] = True
            st.session_state['user'] = user
            st.sidebar.success(f"환영합니다, {username}님!")
        else:
            st.sidebar.error("사용자 이름 또는 비밀번호가 올바르지 않습니다.")

def logout():
    st.sidebar.title("로그아웃")
    if st.sidebar.button("로그아웃"):
        st.session_state['logged_in'] = False
        st.session_state.pop('user', None)
        st.sidebar.success("성공적으로 로그아웃 되었습니다.")
