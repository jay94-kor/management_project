import streamlit as st
import pandas as pd
from streamlit_aggrid import AgGrid, GridOptionsBuilder
from ..components.db import get_budget_data, save_all_budget_data, get_project_names, update_project_name

def edit_project_page():
    st.title("프로젝트 수정")

    project_names = get_project_names()
    selected_project = st.selectbox("수정할 프로젝트를 선택하세요", project_names)

    if selected_project:
        new_project_name = st.text_input("새 프로젝트명", value=selected_project)
        if st.button("프로젝트명 수정"):
            update_project_name(selected_project, new_project_name)
            st.success(f'프로젝트명이 "{selected_project}"에서 "{new_project_name}"으로 변경되었습니다.')
            st.experimental_rerun()

        # 프로젝트 예산 데이터 가져오기
        budget_data = get_budget_data(selected_project)
        gb = GridOptionsBuilder.from_dataframe(budget_data)
        gb.configure_pagination()
        gb.configure_default_column(editable=True)
        grid_options = gb.build()
        grid_response = AgGrid(budget_data, gridOptions=grid_options, editable=True)
        edited_data = grid_response['data']

        if st.button('변경 사항 저장'):
            save_all_budget_data(edited_data)
            st.success('변경 사항이 저장되었습니다.')
            st.experimental_rerun()

        st.write("엑셀에서 데이터를 복사하여 아래에 붙여넣으세요:")
        excel_data = st.text_area("엑셀 데이터 붙여넣기")

        if st.button("데이터 추가"):
            if excel_data:
                try:
                    df = pd.read_clipboard()
                    combined_data = pd.concat([budget_data, df], ignore_index=True)
                    gb = GridOptionsBuilder.from_dataframe(combined_data)
                    gb.configure_pagination()
                    gb.configure_default_column(editable=True)
                    grid_options = gb.build()
                    grid_response = AgGrid(combined_data, gridOptions=grid_options, editable=True)
                    edited_combined_data = grid_response['data']
                    save_all_budget_data(edited_combined_data)
                    st.success("데이터가 추가되었습니다.")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"데이터 추가 중 오류 발생: {e}")
            else:
                st.warning("엑셀 데이터를 붙여넣으세요.")

    if st.button("뒤로가기"):
        st.session_state['edit_project'] = None
        st.experimental_rerun()