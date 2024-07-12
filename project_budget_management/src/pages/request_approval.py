import streamlit as st
from src.components.db import get_db_connection, get_logs
from datetime import datetime

def show():
    st.title("요청 및 승인 시스템")

    conn = get_db_connection()
    c = conn.cursor()

    st.subheader('예산 수정 요청')
    project_id = st.number_input('프로젝트 ID', min_value=1)
    description = st.text_input('요청 내용')
    requested_amount = st.number_input('요청 금액', min_value=0, step=1)

    if st.button('요청 제출'):
        c.execute('INSERT INTO logs (user_id, project_id, action, amount, timestamp) VALUES (?, ?, ?, ?, ?)', 
                  (1, project_id, f"요청: {description}", requested_amount, datetime.now()))
        conn.commit()
        st.success('요청이 제출되었습니다.')

    st.subheader('요청 승인/반려')
    requests = c.execute('SELECT * FROM logs WHERE action LIKE "요청%"').fetchall()
    for request in requests:
        st.write(f"요청 ID: {request['id']}, 프로젝트 ID: {request['project_id']}, 내용: {request['action']}, 금액: {request['amount']}, 시간: {request['timestamp']}")
        if st.button('승인', key=request['id']):
            c.execute('UPDATE logs SET action = ? WHERE id = ?', (f"승인: {request['action']}", request['id']))
            conn.commit()
            st.success('요청이 승인되었습니다.')
        if st.button('반려', key=f"reject-{request['id']}"):
            c.execute('UPDATE logs SET action = ? WHERE id = ?', (f"반려: {request['action']}", request['id']))
            conn.commit()
            st.error('요청이 반려되었습니다.')

    conn.close()