import streamlit as st
from src.components.db import get_db_connection

def show():
    st.title("프로젝트 입력")

    with st.form("project_form"):
        name = st.text_input('프로젝트명', max_chars=100)
        client = st.text_input('클라이언트', max_chars=100)
        created_by = st.text_input('작성자 / 소속', max_chars=100)
        created_at = st.date_input('1차 작성일')
        event_location = st.text_input('행사 장소', max_chars=200)
        final_edit_date = st.date_input('최종 작성일')
        start_date = st.date_input('행사 시작일')
        end_date = st.date_input('행사 종료일')
        category = st.text_input('구분 (대분류)', max_chars=50)
        sub_category = st.text_input('예산과목 (중분류)', max_chars=50)
        item = st.text_input('항목 (소분류)', max_chars=50)
        description = st.text_area('내용', max_chars=500)
        quantity = st.number_input('수량', min_value=0, max_value=1000000, step=1)
        unit = st.text_input('규격', max_chars=50)
        days = st.number_input('일수', min_value=0, max_value=365, step=1)
        times = st.number_input('회', min_value=0, max_value=1000, step=1)
        unit_price = st.number_input('단가', min_value=0, max_value=1000000000, step=1)
        allocated_budget = st.number_input('배정금액', min_value=0, max_value=1000000000, step=1)
        proposed_price = st.number_input('제안가 (VAT포함)', min_value=0, max_value=1000000000, step=1)

        submitted = st.form_submit_button('저장')
        if submitted:
            if not all([name, client, created_by, event_location, category, sub_category, item]):
                st.error('모든 필수 필드를 입력해주세요.')
            elif end_date < start_date:
                st.error('행사 종료일은 시작일 이후여야 합니다.')
            elif allocated_budget > proposed_price:
                st.warning('배정금액이 제안가보다 큽니다. 확인해주세요.')
            else:
                try:
                    conn = get_db_connection()
                    c = conn.cursor()
                    c.execute('''
                        INSERT INTO projects (name, client, created_by, created_at, event_location, final_edit_date, start_date, end_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (name, client, created_by, created_at, event_location, final_edit_date, start_date, end_date))
                    project_id = c.lastrowid
                    c.execute('''
                        INSERT INTO budget_items (project_id, category, sub_category, item, description, quantity, unit, days, times, unit_price, allocated_budget, proposed_price)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (project_id, category, sub_category, item, description, quantity, unit, days, times, unit_price, allocated_budget, proposed_price))
                    conn.commit()
                    st.success('프로젝트와 예산 항목이 추가되었습니다!')
                except Exception as e:
                    st.error(f'오류가 발생했습니다: {str(e)}')
                finally:
                    conn.close()