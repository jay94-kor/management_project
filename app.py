import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
st.cache_data.clear()
st.cache_resource.clear()
import pandas as pd
from services.google_drive import get_project_list
from services.google_sheets import read_sheet_data, sync_data_with_db
from database.db import create_connection, create_table, fetch_all_data, insert_data, update_data, delete_data, fetch_pending_expenses, approve_expense, reject_expense, get_approved_expenses, insert_expense
from utils.openai_utils import classify_data
from utils.account_management import create_user_table, login, register, is_admin, grant_approval_rights
from utils.dashboard import create_dashboard
import plotly.graph_objects as go

@st.cache_data
def process_data_in_chunks(data, chunk_size=1000):
    result = []
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i+chunk_size]
        # 청크 처리 로직
        result.extend(processed_chunk)
    return result

def main():
    st.title("예산 관리 애플리케이션")

    # 사용자 테이블 생성
    create_user_table()

    # 데이터베이스 연결
    conn = create_connection("budget.db")
    create_table(conn)

    # 구글 드라이브 폴더 ID
    folder_id = st.secrets["google_drive"]["folder_id"]

    # 프로젝트 목록 표시
    st.subheader("프로젝트 목록")
    projects = get_project_list(folder_id)
    project_names = [f"{project['name']}" for project in projects]

    cols = st.columns(3)
    for i, project in enumerate(projects):
        with cols[i % 3]:
            st.write(f"### {project['name']}")
            st.write(f"프로젝트 이름: {project['name']}")
            st.write("카테고리 및 배정금액:")
            for category, item, amount in zip(project['categories'], project['items'], project['allocated_amounts']):
                approved_expenses = get_approved_expenses(project['id'], category, item)
                remaining_amount = amount - approved_expenses
                st.write(f"- {category} - {item}: {amount:,.0f}원 (잔액: {remaining_amount:,.0f}원)")
            if st.button(f"지출 추가하기 - {project['name']}", key=f"add_expense_{project['name']}_{i}"):
                st.session_state.selected_project = project
                st.experimental_rerun()

    if 'selected_project' in st.session_state:
        selected_project = st.session_state.selected_project
        st.write(f"선택된 프로젝트: {selected_project['name']}")

        # 지출 추가 폼
        st.subheader("지출 추가")
        category = st.selectbox("카테고리", selected_project['categories'])
        item_index = selected_project['categories'].index(category)
        item = selected_project['items'][item_index]
        st.write(f"선택된 항목: {item}")
        allocated_amount = selected_project['allocated_amounts'][item_index]
        st.write(f"배정금액: {allocated_amount:,.0f}원")
        
        amount = st.number_input("지출 금액", min_value=0.0, max_value=float(allocated_amount))
        description = st.text_area("설명")

        if st.button("지출 추가"):
            new_expense = {
                'project_id': selected_project['id'],
                'category': category,
                'item': item,
                'amount': amount,
                'description': description,
                'status': 'pending'
            }
            insert_expense(new_expense)
            st.success("지출이 성공적으로 추가되었습니다.")
            del st.session_state.selected_project
            st.experimental_rerun()

        # 승인 프로세스
        if 'user' in st.session_state and is_admin(st.session_state.user):
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

        # Google Sheets 동기화
        if st.button('Google Sheets와 동기화'):
            spreadsheet_id = st.session_state.get('spreadsheet_id')
            if spreadsheet_id:
                sync_data_with_db(spreadsheet_id, lambda: fetch_all_data(conn))
                st.success("데이터가 Google Sheets와 동기화되었습니다")
            else:
                st.error("스프레드시트 ID를 찾을 수 없습니다.")

        # 관리자 기능
        if 'user' in st.session_state and is_admin(st.session_state.user):
            st.subheader("관리자 기능")
            user_to_grant = st.text_input("승인 권한을 부여할 사용자명")
            if st.button("승인 권한 부여"):
                if grant_approval_rights(user_to_grant):
                    st.success(f"{user_to_grant}에게 승인 권한이 부여되었습니다.")
                else:
                    st.error("승인 권한 부여에 실패했습니다.")

        # 로그아웃
        if 'user' in st.session_state and st.button("로그아웃"):
            del st.session_state.user
            st.experimental_rerun()

        # 프로젝트 예산 사용 현황 대시보드
        create_budget_dashboard(selected_project)

    # 프로젝트 간 예산 비교 대시보드
    if st.button("프로젝트 간 예산 비교"):
        create_projects_comparison_dashboard(projects)

    # 예산 경고 체크
    if 'user' in st.session_state and is_admin(st.session_state.user):
        st.subheader("예산 경고")
        for project in projects:
            warnings = check_budget_warnings(project)
            if warnings:
                st.write(f"{project['name']} 예산 경고:")
                for warning in warnings:
                    st.warning(warning)

def create_budget_dashboard(project):
    st.subheader(f"{project['name']} 예산 사용 현황")
    
    categories = project['categories']
    allocated_amounts = project['allocated_amounts']
    used_amounts = [get_approved_expenses(project['id'], cat, item) for cat, item in zip(project['categories'], project['items'])]
    remaining_amounts = [alloc - used for alloc, used in zip(allocated_amounts, used_amounts)]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=categories, y=used_amounts, name='사용금액'))
    fig.add_trace(go.Bar(x=categories, y=remaining_amounts, name='잔액'))
    
    fig.update_layout(barmode='stack', title='카테고리별 예산 사용 현황')
    st.plotly_chart(fig)
    
    # 전체 예산 대비 사용 금액 비율
    total_budget = sum(allocated_amounts)
    total_used = sum(used_amounts)
    usage_ratio = (total_used / total_budget) * 100
    
    st.write(f"전체 예산: {total_budget:,.0f}원")
    st.write(f"사용 금액: {total_used:,.0f}원")
    st.write(f"사용 비율: {usage_ratio:.2f}%")
    
    # 프로그레스 바로 사용 비율 표시
    st.progress(usage_ratio / 100)

def create_projects_comparison_dashboard(projects):
    st.subheader("프로젝트 간 예산 비교")
    
    project_names = [p['name'] for p in projects]
    total_budgets = [sum(p['allocated_amounts']) for p in projects]
    used_budgets = [sum([get_approved_expenses(p['id'], cat, item) for cat, item in zip(p['categories'], p['items'])]) for p in projects]
    remaining_budgets = [total - used for total, used in zip(total_budgets, used_budgets)]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=project_names, y=used_budgets, name='사용금액'))
    fig.add_trace(go.Bar(x=project_names, y=remaining_budgets, name='잔액'))
    
    fig.update_layout(barmode='stack', title='프로젝트별 예산 사용 현황')
    st.plotly_chart(fig)
    
    # 프로젝트별 예산 사용 비율 표시
    for name, total, used in zip(project_names, total_budgets, used_budgets):
        usage_ratio = (used / total) * 100
        st.write(f"{name}: {usage_ratio:.2f}% 사용")
        st.progress(usage_ratio / 100)

def check_budget_warnings(project):
    warnings = []
    for category, item, allocated in zip(project['categories'], project['items'], project['allocated_amounts']):
        used = get_approved_expenses(project['id'], category, item)
        if used > allocated:
            warnings.append(f"{category} - {item}: 예산 초과 (배정: {allocated:,.0f}원, 사용: {used:,.0f}원)")
    return warnings

if __name__ == "__main__":
    main()
    main()