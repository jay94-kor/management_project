import streamlit as st

def project_form():
    with st.form("project_form"):
        name = st.text_input('프로젝트명')
        client = st.text_input('클라이언트')
        created_by = st.text_input('작성자 / 소속')
        created_at = st.date_input('1차 작성일')
        event_location = st.text_input('행사 장소')
        final_edit_date = st.date_input('최종 작성일')
        start_date = st.date_input('행사 시작일')
        end_date = st.date_input('행사 종료일')

        submitted = st.form_submit_button('저장')
        if submitted:
            return {
                "name": name,
                "client": client,
                "created_by": created_by,
                "created_at": created_at,
                "event_location": event_location,
                "final_edit_date": final_edit_date,
                "start_date": start_date,
                "end_date": end_date
            }
    return None
