import streamlit as st
from services.project_service import get_projects, add_expense, fetch_pending_expenses
from services.google_sheets_service import sync_data_with_sheets
from utils.dashboard import create_budget_dashboard, create_projects_comparison_dashboard
from utils.account_management import login, register, is_admin, grant_approval_rights
from utils.budget_warnings import check_budget_warnings

st.set_page_config(page_title="예산 관리 애플리케이션", layout="wide")

def main():
    st.title("예산 관리 애플리케이션")

    if 'user' not in st.session_state:
        show_login_register()
    else:
        show_main_app()

def show_login_register():
    tab1, tab2 = st.tabs(["로그인", "회원가입"])
    
    with tab1:
        username = st.text_input("사용자명")
        password = st.text_input("비밀번호", type="password")
        if st.button("로그인"):
            if login(username, password):
                st.session_state.user = username
                st.experimental_rerun()
            else:
                st.error("로그인 실패")

    with tab2:
        new_username = st.text_input("새 사용자명")
        new_password = st.text_input("새 비밀번호", type="password")
        if st.button("회원가입"):
            if register(new_username, new_password):
                st.success("회원가입 성공")
            else:
                st.error("회원가입 실패")

def show_main_app():
    projects = get_projects()
    
    st.sidebar.title("메뉴")
    menu = st.sidebar.radio("선택", ["프로젝트 목록", "지출 추가", "승인 대기 지출", "예산 대시보드", "프로젝트 비교", "관리자 기능"])

    if menu == "프로젝트 목록":
        show_projects(projects)
    elif menu == "지출 추가":
        show_add_expense(projects)
    elif menu == "승인 대기 지출":
        show_pending_expenses()
    elif menu == "예산 대시보드":
        show_budget_dashboard(projects)
    elif menu == "프로젝트 비교":
        show_projects_comparison(projects)
    elif menu == "관리자 기능":
        show_admin_functions()

    if st.sidebar.button("로그아웃"):
        del st.session_state.user
        st.experimental_rerun()

def show_projects(projects):
    st.subheader("프로젝트 목록")
    for project in projects:
        st.write(f"### {project['name']}")
        st.write(f"프로젝트 이름: {project['name']}")
        st.write("카테고리 및 배정금액:")
        for category, item, amount, remaining in zip(project['categories'], project['items'], project['allocated_amounts'], project['remaining_amounts']):
            st.write(f"- {category} - {item}: {amount:,.0f}원 (잔액: {remaining:,.0f}원)")

def show_add_expense(projects):
    st.subheader("지출 추가")
    project = st.selectbox("프로젝트 선택", projects, format_func=lambda x: x['name'])
    category = st.selectbox("카테고리", project['categories'])
    item_index = project['categories'].index(category)
    item = project['items'][item_index]
    allocated_amount = project['allocated_amounts'][item_index]
    remaining_amount = project['remaining_amounts'][item_index]

    st.write(f"선택된 항목: {item}")
    st.write(f"배정금액: {allocated_amount:,.0f}원")
    st.write(f"잔액: {remaining_amount:,.0f}원")

    amount = st.number_input("지출 금액", min_value=0.0, max_value=float(remaining_amount))
    description = st.text_area("설명")

    if st.button("지출 추가"):
        add_expense(project['id'], category, item, amount, description)
        st.success("지출이 성공적으로 추가되었습니다.")

def show_pending_expenses():
    if is_admin(st.session_state.user):
        st.subheader("승인 대기 중인 지출")
        pending_expenses = fetch_pending_expenses()
        for expense in pending_expenses:
            st.write(f"프로젝트: {expense['project_name']}")
            st.write(f"카테고리: {expense['category']}")
            st.write(f"항목: {expense['item']}")
            st.write(f"금액: {expense['amount']:,.0f}원")
            st.write(f"설명: {expense['description']}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"승인 - {expense['id']}", key=f"approve_{expense['id']}"):
                    approve_expense(expense['id'])
                    st.success("지출이 승인되었습니다.")
                    st.experimental_rerun()
            with col2:
                if st.button(f"거부 - {expense['id']}", key=f"reject_{expense['id']}"):
                    reject_expense(expense['id'])
                    st.error("지출이 거부되었습니다.")
                    st.experimental_rerun()
    else:
        st.warning("관리자 권한이 필요합니다.")

def show_budget_dashboard(projects):
    st.subheader("예산 대시보드")
    project = st.selectbox("프로젝트 선택", projects, format_func=lambda x: x['name'])
    create_budget_dashboard(project)

def show_projects_comparison(projects):
    st.subheader("프로젝트 간 예산 비교")
    create_projects_comparison_dashboard(projects)

def show_admin_functions():
    if is_admin(st.session_state.user):
        st.subheader("관리자 기능")
        user_to_grant = st.text_input("승인 권한을 부여할 사용자명")
        if st.button("승인 권한 부여"):
            if grant_approval_rights(user_to_grant):
                st.success("승인 권한이 부여되었습니다.")
            else:
                st.error("승인 권한 부여에 실패했습니다.")

        if st.button("Google Sheets와 동기화"):
            sync_data_with_sheets()
            st.success("데이터가 Google Sheets와 동기화되었습니다")

        st.subheader("예산 경고")
        for project in projects:
            warnings = check_budget_warnings(project)
            if warnings:
                st.write(f"{project['name']} 예산 경고:")
                for warning in warnings:
                    st.warning(warning)
    else:
        st.warning("관리자 권한이 필요합니다.")

if __name__ == "__main__":
    main()