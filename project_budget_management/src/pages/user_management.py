import streamlit as st
from project_budget_management.src.components.db import get_db_connection, get_users
from project_budget_management.src.components.auth import hash_password

def show():
    st.title("회원 관리")

    conn = get_db_connection()
    c = conn.cursor()

    st.subheader('회원 계정 추가')
    username = st.text_input('사용자 이름')
    password = st.text_input('비밀번호', type='password')
    role = st.selectbox('역할', ['user', 'admin'])

    if st.button('계정 추가'):
        hashed_password = hash_password(password)
        c.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', (username, hashed_password, role))
        conn.commit()
        st.success('회원 계정이 추가되었습니다.')

    st.subheader('회원 목록 및 권한 부여')
    users = get_users()
    for user in users:
        st.write(f"ID: {user['id']}, 이름: {user['username']}, 역할: {user['role']}")
        new_role = st.selectbox(f"권한 변경 (현재: {user['role']})", ['user', 'admin'], index=['user', 'admin'].index(user['role']), key=user['id'])
        if st.button('권한 변경', key=f"change-{user['id']}"):
            c.execute('UPDATE users SET role = ? WHERE id = ?', (new_role, user['id']))
            conn.commit()
            st.success('회원 권한이 변경되었습니다.')

    conn.close()