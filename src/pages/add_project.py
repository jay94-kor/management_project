import streamlit as st
import pandas as pd
from streamlit_aggrid import AgGrid, GridOptionsBuilder
from ..components.db import add_project, save_all_budget_data

def add_project_page():
    st.title("프로젝트 추가")

    with st.form(key='add_project_form'):
        new_project = st.text_input('새 프로젝트명')
        add_project_submit = st.form_submit_button('프로젝트 추가')

        if add_project_submit:
            if new_project:
                try:
                    add_project(new_project)
                    st.success(f'프로젝트 "{new_project}"가 추가되었습니다.')
                    st.experimental_rerun()
                except ValueError as e:
                    st.error(str(e))
            else:
                st.warning('프로젝트명을 입력하세요.')

    st.write("엑셀에서 데이터를 복사하여 아래에 붙여넣으세요:")
    excel_data = st.text_area("엑셀 데이터 붙여넣기")

    if st.button("데이터 저장"):
        if excel_data:
            try:
                df = pd.read_clipboard()
                gb = GridOptionsBuilder.from_dataframe(df)
                gb.configure_pagination()
                gb.configure_default_column(editable=True)
                grid_options = gb.build()
                grid_response = AgGrid(df, gridOptions=grid_options, editable=True)
                edited_data = grid_response['data']
                save_all_budget_data(edited_data)
                st.success("데이터가 저장되었습니다.")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"데이터 저장 중 오류 발생: {e}")
        else:
            st.warning("엑셀 데이터를 붙여넣으세요.")

    if st.button("뒤로가기"):
        st.session_state['add_project'] = False
        st.experimental_rerun()