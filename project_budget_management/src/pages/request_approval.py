import streamlit as st
from ..components.db import get_db_connection, get_logs
from datetime import datetime

def show():
    st.title("요청 및 승인 시스템")

    conn = get_db_connection()
    c = conn.cursor()

    user_role = st.session_state.get('user_role', 'user')  # 기본값은 'user'로 설정

    if user_role == 'user':
        st.subheader('예산 수정 요청')
        project_id = st.number_input('프로젝트 ID', min_value=1)
        description = st.text_input('요청 내용')
        requested_amount = st.number_input('요청 금액', min_value=0, step=1)

        if st.button('요청 제출'):
            user_id = st.session_state.get('user_id', 1)  # 실제 사용자 ID로 변경 필요
            c.execute('INSERT INTO logs (user_id, project_id, action, amount, timestamp) VALUES (?, ?, ?, ?, ?)', 
                      (user_id, project_id, f"요청: {description}", requested_amount, datetime.now()))
            conn.commit()
            st.success('요청이 제출되었습니다.')

    elif user_role == 'admin':
        st.subheader('요청 승인/반려')
        requests = c.execute('SELECT * FROM logs WHERE action LIKE "요청%"').fetchall()
        for request in requests:
            st.write(f"요청 ID: {request['id']}, 프로젝트 ID: {request['project_id']}, 내용: {request['action']}, 금액: {request['amount']}, 시간: {request['timestamp']}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button('승인', key=f"approve-{request['id']}"):
                    c.execute('UPDATE logs SET action = ? WHERE id = ?', (f"승인: {request['action']}", request['id']))
                    conn.commit()
                    st.success('요청이 승인되었습니다.')
            with col2:
                if st.button('반려', key=f"reject-{request['id']}"):
                    c.execute('UPDATE logs SET action = ? WHERE id = ?', (f"반려: {request['action']}", request['id']))
                    conn.commit()
                    st.error('요청이 반려되었습니다.')

    conn.close()