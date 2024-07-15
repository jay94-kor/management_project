import streamlit as st
import pandas as pd
from utils.db_utils import setup_database
from services.project_service import get_projects, get_project_items, add_expenditure_request, update_project_budget, get_expenditure_requests, get_project_by_id, get_project_expenditures, cancel_expenditure_request
from services.expenditure_service import approve_expenditure, reject_expenditure
import time

def sidebar_menu():
    st.sidebar.title("메뉴")
    menu = st.sidebar.radio("", ["대시보드", "프로젝트 목록", "지출 승인"])
    return menu

def display_dashboard():
    st.header("대시보드")
    projects = get_projects()
    total_projects = len(projects)
    total_contract_amount = sum(int(project[6]) for project in projects)
    total_expected_profit = sum(int(project[7]) for project in projects)

    col1, col2, col3 = st.columns(3)
    col1.metric("총 프로젝트 수", f"{total_projects}개")
    col2.metric("총 계약금액", format_currency(total_contract_amount))
    col3.metric("예상 총 수익", format_currency(total_expected_profit))
    
    st.subheader("프로젝트 현황")
    df = pd.DataFrame(projects, columns=["ID", "프로젝트 코드", "이름", "고객사", "PM", "부서", "계약금액", "예상수익", "수익률"])
    df['계약금액'] = df['계약금액'].apply(format_currency)
    df['예상수익'] = df['예상수익'].apply(format_currency)
    df['수익률'] = df['수익률'].apply(lambda x: f"{x*100:.0f}%")
    st.dataframe(df)

def display_project_cards():
    st.header("프로젝트 목록")
    projects = get_projects()
    cols = st.columns(3)
    for idx, project in enumerate(projects):
        with cols[idx % 3]:
            with st.expander(project[2], expanded=True):
                st.write(f"계약금액: {format_currency(project[6])}")
                st.write(f"수익률: {project[8]*100:.0f}%" if project[8] is not None else "수익률: N/A")
                st.write(f"담당자: {project[4]}")
                if st.button("상세 보기", key=f"view_{project[1]}"):
                    st.session_state.selected_project = project[1]

def display_project_details(project_code):
    project = get_project_by_id(project_code)
    if not project:
        st.error("프로젝트를 찾을 수 없습니다.")
        return

    st.subheader(f"프로젝트 코드: {project[1]} - 프로젝트: {project[2]}")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("계약금액", format_currency(int(project[6])))
    col2.metric("예상 수익", format_currency(int(project[7])))
    col3.metric("수익률", f"{project[8]*100:.0f}%" if project[8] is not None else "N/A")

    st.write(f"**고객사:** {project[3]}")
    st.write(f"**PM:** {project[4]}")
    st.write(f"**부서:** {project[5]}")

    st.subheader("프로젝트 항목")
    items = get_project_items(project_code)
    if items:
        df = pd.DataFrame(items, columns=["ID", "프로젝트ID", "프로젝트 코드", "카테고리", "항목명", "설명", "수량1", "규격1", "수량2", "규격2", "단가", "총액", "배정금액", "총 지출액"])
        st.dataframe(df)
    else:
        st.info("해당 프로젝트에 등록된 항목이 없습니다.")

    st.subheader("지출 내역")
    expenditures = get_project_expenditures(project_code)
    if expenditures:
        exp_df = pd.DataFrame(expenditures, columns=["ID", "프로젝트ID", "프로젝트 코드", "금액", "지출처", "사유", "지출 예정일", "파일명", "파일 내용", "상태", "생성일"])
        st.dataframe(exp_df)
    else:
        st.info("해당 프로젝트의 지출 내역이 없습니다.")

def expenditure_request_form(project_code):
    st.subheader("지출 요청")
    project_items = get_project_items(project_code)
    
    if not project_items:
        st.info("이 프로젝트에 등록된 항목이 없습니다.")
        return
    
    item_options = [f"{item[4]} (잔액: {format_currency(item[12] - item[13])})" for item in project_items]
    
    with st.form("expenditure_request"):
        selected_item = st.selectbox("항목 선택", item_options)
        selected_item_index = item_options.index(selected_item)
        selected_item_data = project_items[selected_item_index]
        remaining_budget = selected_item_data[12] - selected_item_data[13]
        
        st.write(f"잔여 예산: {format_currency(remaining_budget)}")
        
        amount_str = st.text_input("지출액", value="0")
        amount_str = amount_str.replace(',', '')  # 콤마 제거
        try:
            amount = int(amount_str)
        except ValueError:
            st.error("올바른 금액을 입력해주세요.")
            return
        
        st.write(f"입력한 금액: {format_currency(amount)}")
        
        expenditure_type = st.text_input("지출처")  # 협력사 이름 입력
        reason = st.text_area("지출 사유")
        date = st.date_input("지출 예정일")
        attachment = st.file_uploader("첨부 파일", type=["pdf", "jpg", "png"])
        submitted = st.form_submit_button("상신")
        
        if submitted:
            if amount > remaining_budget:
                st.error("잔여 예산을 초과하는 금액입니다.")
                return
            
            if attachment:
                file_contents = attachment.read()
                file_name = attachment.name
            else:
                file_contents = None
                file_name = None
            selected_item_id = selected_item_data[0]
            add_expenditure_request(selected_item_id, amount, expenditure_type, reason, date, file_name, file_contents)
            st.success("지출 요청이 상신되었습니다.")
            st.balloons()  # 추가: 상신 완료 시 풍선 효과
            time.sleep(2)  # 2초 대기
            st.experimental_rerun()

    st.subheader("상신된 지출 요청")
    expenditures = get_project_expenditures(project_code)
    pending_expenditures = [exp for exp in expenditures if exp[9] == 'Pending']
    
    if pending_expenditures:
        for exp in pending_expenditures:
            with st.expander(f"요청 ID: {exp[0]} - 금액: {format_currency(exp[3])}"):
                st.write(f"지출처: {exp[4]}")
                st.write(f"사유: {exp[5]}")
                st.write(f"지출 예정일: {exp[6]}")
                if st.button("취소", key=f"cancel_{exp[0]}"):
                    cancel_expenditure_request(exp[0])
                    st.success("지출 요청이 취소되었습니다.")
                    st.experimental_rerun()
    else:
        st.info("상신된 지출 요청이 없습니다.")

def approve_expenditure_requests():
    st.header("지출 승인")
    expenditure_requests = get_expenditure_requests()
    for request in expenditure_requests:
        with st.expander(f"요청 ID: {request[0]} - 금액: {request[2]:,.0f}원"):
            st.write(f"프로젝트: {request[1]}")
            st.write(f"지출처: {request[3]}")
            st.write(f"사유: {request[4]}")
            st.write(f"지출 예정일: {request[5]}")
            if request[6]:  # 첨부 파일이 있는 경우
                st.download_button("첨부 파일 다운로드", request[7], file_name=request[6])
            col1, col2 = st.columns(2)
            with col1:
                if st.button("승인", key=f"approve_{request[0]}"):
                    approve_expenditure(request[0])
                    st.success("지출이 승인되었습니다.")
                    st.experimental_rerun()
            with col2:
                if st.button("반려", key=f"reject_{request[0]}"):
                    reject_expenditure(request[0])
                    st.success("지출이 반려되었습니다.")
                    st.experimental_rerun()

def main():
    st.set_page_config(layout="wide", page_title="프로젝트 관리 시스템")
    
    if 'selected_project' not in st.session_state:
        st.session_state.selected_project = None
    
    menu = sidebar_menu()
    
    if menu == "대시보드":
        display_dashboard()
    elif menu == "프로젝트 목록":
        display_project_cards()
        if st.session_state.selected_project:
            st.header(f"프로젝트 상세 정보 (ID: {st.session_state.selected_project})")
            display_project_details(st.session_state.selected_project)
            expenditure_request_form(st.session_state.selected_project)
    elif menu == "지출 승인":
        approve_expenditure_requests()

def format_currency(amount):
    amount = int(amount)  # 소수점 제거
    if amount >= 100000000:
        if (amount % 100000000) == 0:
            return f"{amount // 100000000}억원"
        else:
            return f"{amount // 100000000}억 {((amount % 100000000) // 10000):,}만원"
    else:
        return f"{(amount // 10000):,}만원"

if __name__ == "__main__":
    setup_database()
    main()