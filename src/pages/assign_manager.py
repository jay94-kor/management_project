import streamlit as st
from ..components.db import get_budget_data, add_budget_entry, get_project_names
from ..components.common import validate_data

def assign_manager_page():
    st.title("프로젝트 예산 관리")

    # 프로젝트명 선택
    project_names = get_project_names()
    if not project_names:
        st.warning("프로젝트가 없습니다. 새 프로젝트를 추가하세요.")
        return

    selected_project = st.selectbox('프로젝트명 선택', project_names)
    
    # 선택한 프로젝트의 데이터 필터링
    project_data = get_budget_data(selected_project)
    
    # 데이터프레임 표시
    st.dataframe(project_data)

    # 입력 폼 작성
    with st.form(key='update_form'):
        구분 = st.text_input('구분')
        예산과목 = st.text_input('예산과목')
        항목 = st.text_input('항목')
        내용 = st.text_input('내용')
        수량 = st.number_input('수량', min_value=0)
        규격 = st.text_input('규격')
        일수 = st.number_input('일수', min_value=0)
        일수_규격 = st.text_input('일수 규격')
        회 = st.number_input('회', min_value=0)
        회_규격 = st.text_input('회 규격')
        단가 = st.number_input('단가', min_value=0)
        배정_금액 = st.number_input('배정 금액', min_value=0)
        수주금액 = st.number_input('수주금액', min_value=0)
        제출 = st.form_submit_button('제출')

        if 제출:
            new_data = (
                selected_project, 구분, 예산과목, 항목, 내용, 수량, 규격, 일수, 일수_규격, 회, 회_규격, 단가, 배정_금액, 수주금액
            )
            if validate_data(new_data):
                add_budget_entry(new_data)
                st.success('데이터가 추가되었습니다.')
                st.experimental_rerun()
