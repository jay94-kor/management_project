import streamlit as st
from pages import home, project_input, project_list, project_budget, dashboard, request_approval, user_management, budget_adjustment, project_budget_adjustment, assign_manager, margin_maintenance
from components.auth import login, logout

st.set_page_config(
    page_title="프로젝트 예산 관리 시스템",
    page_icon=":money_with_wings:",
    layout="wide"
)

# 로그인 상태 확인
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if st.session_state['logged_in']:
    user_role = st.session_state['user'][3]  # 역할을 세션 상태에서 가져옴
    st.session_state['user_role'] = user_role
    st.session_state['user_id'] = st.session_state['user'][0]  # 사용자 ID를 세션 상태에 저장

    st.sidebar.title("메뉴")
    menu_items = ["홈", "프로젝트 입력", "프로젝트 목록", "프로젝트 예산 관리", "대시보드", "요청 및 승인 시스템", "항목별 예산 이동", "프로젝트 간 예산 이동", "담당자 지정", "마진율 유지"]
    if user_role == 'admin':
        menu_items.append("회원 관리")
    page = st.sidebar.selectbox("페이지 선택", menu_items)
    logout()

    if page == "홈":
        home.show()
    elif page == "프로젝트 입력":
        project_input.show()
    elif page == "프로젝트 목록":
        project_list.show()
    elif page == "프로젝트 예산 관리":
        project_budget.show()
    elif page == "대시보드":
        dashboard.show()
    elif page == "요청 및 승인 시스템":
        request_approval.show()
    elif page == "회원 관리" and user_role == 'admin':
        user_management.show()
    elif page == "항목별 예산 이동":
        budget_adjustment.show()
    elif page == "프로젝트 간 예산 이동":
        project_budget_adjustment.show()
    elif page == "담당자 지정":
        assign_manager.show()
    elif page == "마진율 유지":
        margin_maintenance.show()
else:
    login()