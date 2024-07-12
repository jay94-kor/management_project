import streamlit as st
import pandas as pd
from utils.db_utils import setup_database
from services.project_service import get_projects, get_project_items, add_expenditure_request, update_project_budget, get_expenditure_requests
from services.expenditure_service import approve_expenditure

def display_project_cards():
    projects = get_projects()
    cols = st.columns(3)
    for idx, project in enumerate(projects):
        with cols[idx % 3]:
            with st.expander(project[1], expanded=False):
                st.write(f"계약금액: {project[5]:,.0f}원")
                st.write(f"수익률: {project[7]:.2f}%" if project[7] is not None else "수익률: N/A")
                st.write(f"담당자: {project[3]}")
                if st.button("상세 보기", key=f"view_{project[0]}"):
                    st.session_state.selected_project = project[0]

def display_project_details(project_id):
    items = get_project_items(project_id)
    if items:
        df = pd.DataFrame(items, columns=["ID", "프로젝트ID", "카테고리", "항목명", "설명", "수량1", "규격1", "수량2", "규격2", "단가", "총액", "배정금액"])
        st.dataframe(df)
    else:
        st.info("해당 프로젝트에 등록된 항목이 없습니다.")

def expenditure_request_form(project_id):
    st.subheader("지출 요청")
    with st.form("expenditure_request"):
        amount = st.number_input("지출액", min_value=0.0, step=1000.0)
        expenditure_type = st.selectbox("지출처", ["인건비", "협력사"])
        reason = st.text_area("지출 사유")
        submitted = st.form_submit_button("상신")
        if submitted:
            add_expenditure_request(project_id, amount, expenditure_type, reason)
            st.success("지출 요청이 상신되었습니다.")
            st.experimental_rerun()

def approve_expenditure_requests():
    st.subheader("지출 승인")
    expenditure_requests = get_expenditure_requests()
    for request in expenditure_requests:
        with st.expander(f"요청 ID: {request[0]} - 금액: {request[2]:,.0f}원"):
            st.write(f"프로젝트: {request[1]}")
            st.write(f"지출처: {request[3]}")
            st.write(f"사유: {request[4]}")
            if st.button("승인", key=f"approve_{request[0]}"):
                approve_expenditure(request[0])
                st.success("지출이 승인되었습니다.")
                st.experimental_rerun()

def main():
    st.title("프로젝트 관리 시스템")
    
    if 'selected_project' not in st.session_state:
        st.session_state.selected_project = None
    
    display_project_cards()
    
    if st.session_state.selected_project:
        st.header(f"프로젝트 상세 정보 (ID: {st.session_state.selected_project})")
        display_project_details(st.session_state.selected_project)
        expenditure_request_form(st.session_state.selected_project)
    
    approve_expenditure_requests()

if __name__ == "__main__":
    setup_database()
    main()