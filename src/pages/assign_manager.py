import streamlit as st
import pandas as pd
from ..components.db import get_all_budget_data, save_all_budget_data, get_project_names, add_project

def assign_manager_page():
    st.title("프로젝트 예산 관리")

    project_names = get_project_names()
    if not project_names:
        st.warning("프로젝트가 없습니다. 새 프로젝트를 추가하세요.")
        return

    # 전체 데이터 가져오기
    all_data = get_all_budget_data()

    # 데이터 편집
    edited_data = st.data_editor(all_data)

    if st.button('변경 사항 저장'):
        save_all_budget_data(edited_data)
        st.success('변경 사항이 저장되었습니다.')
        st.experimental_rerun()