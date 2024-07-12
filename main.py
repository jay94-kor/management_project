import streamlit as st
import pandas as pd
from utils.db_utils import setup_database
from services.project_service import add_project, get_projects, add_project_item, get_project_items, update_project_budget
from services.expenditure_service import request_expenditure, approve_expenditure
import csv
import io

# 상수 정의
MENU_PROJECT_ADD = "프로젝트 추가"
MENU_PROJECT_ITEM_ADD = "프로젝트 항목 추가"
MENU_EXPENDITURE_REQUEST = "지출 신청"
MENU_EXPENDITURE_APPROVE = "지출 승인"
MENU_PROJECT_DETAIL = "프로젝트 상세 조회"
MENU_BULK_IMPORT = "대량 데이터 입력"

def display_projects():
    st.header("프로젝트 목록")
    projects = get_projects()
    if projects:
        columns = ["ID", "프로젝트 이름", "발주처", "담당자", "소속", "계약금액", "예상이익", "예상이익률"]
        df = pd.DataFrame(projects, columns=columns[:-1])
        df["예상이익률"] = df["예상이익"] / df["계약금액"] * 100
        df["예상이익률"] = df["예상이익률"].apply(lambda x: f"{x:.2f}%")
        st.dataframe(df)
    else:
        st.info("등록된 프로젝트 없습니다.")

def add_project_menu():
    st.header(MENU_PROJECT_ADD)
    with st.form("project_add_form"):
        name = st.text_input("프로젝트 이름", max_chars=100)
        company = st.text_input("발주처", max_chars=100)
        manager = st.text_input("담당���", max_chars=50)
        department = st.text_input("소속", max_chars=50)
        total_budget = st.number_input("총 예산", min_value=0)
        current_budget = st.number_input("현재 예산", min_value=0, max_value=total_budget)
        submitted = st.form_submit_button("프로젝트 추가")
        
    if submitted:
        try:
            add_project(name, company, manager, department, total_budget, current_budget)
            st.success("프로젝트가 추가되었습니다.")
            st.experimental_rerun()
        except Exception as e:
            st.error(f"프로젝트 추가 중 오류가 발생했습니다: {str(e)}")

def add_project_item_menu():
    st.header(MENU_PROJECT_ITEM_ADD)
    projects = get_projects()
    project_ids = [project[0] for project in projects]
    project_names = [project[1] for project in projects]
    
    selected_project_id = st.selectbox("프로젝트 선택", options=project_ids, format_func=lambda x: project_names[project_ids.index(x)])
    
    if selected_project_id:
        with st.form("project_item_add_form"):
            category = st.text_input("카테고리", max_chars=50)
            item_name = st.text_input("항목명", max_chars=100)
            description = st.text_area("설명", max_chars=500)
            quantity = st.number_input("수량", min_value=1, step=1)
            unit = st.text_input("단위", max_chars=20)
            period = st.number_input("기간", min_value=1, step=1)
            period_unit = st.text_input("기간 단위", max_chars=20)
            unit_price = st.number_input("단가", min_value=0)
            total_price = st.number_input("총액", min_value=0)
            submitted = st.form_submit_button("항목 추가")
        
        if submitted:
            try:
                add_project_item(selected_project_id, category, item_name, description, quantity, unit, period, period_unit, unit_price, total_price)
                st.success("프로젝트 항목이 추가되었습니다.")
            except Exception as e:
                st.error(f"프로젝트 항목 추가 중 오류가 발생했습니다: {str(e)}")
    else:
        st.warning("프로젝트를 먼저 선택해주세요.")

def request_expenditure_menu():
    st.header(MENU_EXPENDITURE_REQUEST)
    projects = get_projects()
    project_ids = [project[0] for project in projects]
    project_names = [project[1] for project in projects]
    
    with st.form("expenditure_request_form"):
        project_id = st.selectbox("프로젝트", options=project_ids, format_func=lambda x: project_names[project_ids.index(x)])
        amount = st.number_input("금액", min_value=0)
        submitted = st.form_submit_button("지출 신청")
    
    if submitted:
        try:
            request_expenditure(project_id, amount)
            st.success("지출이 신청되었습니다.")
        except Exception as e:
            st.error(f"지출 신청 중 오류가 발생했습니다: {str(e)}")

def approve_expenditure_menu():
    st.header(MENU_EXPENDITURE_APPROVE)
    with st.form("expenditure_approve_form"):
        expenditure_id = st.number_input("지출 ID", min_value=1, step=1)
        submitted = st.form_submit_button("지출 승인")
    
    if submitted:
        try:
            approve_expenditure(expenditure_id)
            st.success("지출이 승인되었습니다.")
        except Exception as e:
            st.error(f"지출 승인 중 오류가 발생했습니다: {str(e)}")

def project_detail_menu():
    st.header(MENU_PROJECT_DETAIL)
    projects = get_projects()
    project_ids = [project[0] for project in projects]
    project_names = [project[1] for project in projects]
    
    project_id = st.selectbox("프로젝트", options=project_ids, format_func=lambda x: project_names[project_ids.index(x)])
    if st.button("프로젝트 항목 조회"):
        try:
            project_items = get_project_items(project_id)
            if project_items:
                df = pd.DataFrame(project_items, columns=["ID", "프로젝트ID", "카테고리", "항목명", "설명", "수량", "단위", "기간", "기간 단위", "단가", "총액", "배정금액"])
                st.dataframe(df)
            else:
                st.info("해당 프로젝트에 등록된 항목이 없습니다.")
        except Exception as e:
            st.error(f"프로젝트 항목 조회 중 오류가 발생했습니다: {str(e)}")

def bulk_import_menu():
    st.header(MENU_BULK_IMPORT)
    
    uploaded_file = st.file_uploader("CSV 파일 업로드", type="csv")
    if uploaded_file is not None:
        content = uploaded_file.getvalue().decode('utf-8')
        csv_data = csv.reader(io.StringIO(content))
        next(csv_data)  # 헤더 행 건너뛰기
        
        for row in csv_data:
            try:
                name, client, pm, department, contract_amount, expected_profit = row
                # 쉼표 제거 및 공백 제거
                contract_amount = float(contract_amount.replace(',', '').strip())
                expected_profit = float(expected_profit.replace(',', '').strip())
                add_project(name, client, pm, department, contract_amount, expected_profit)
                st.success(f"���로젝트 '{name}'가 추가되었습니다.")
            except Exception as e:
                st.error(f"프로젝트 '{name}' 추가 중 오류 발생: {str(e)}")
        
        st.success("모든 데이터가 처리되었습니다.")

def bulk_import_project_items_menu():
    st.header("프로젝트 항목 대량 추가")
    projects = get_projects()
    project_ids = [project[0] for project in projects]
    project_names = [project[1] for project in projects]
    
    selected_project_id = st.selectbox("프로젝트 선택", options=project_ids, format_func=lambda x: project_names[project_ids.index(x)])
    
    if selected_project_id:
        uploaded_file = st.file_uploader("CSV 파일 업로드", type="csv")
        if uploaded_file is not None:
            content = uploaded_file.getvalue().decode('utf-8')
            csv_data = csv.reader(io.StringIO(content))
            next(csv_data)  # 헤더 행 건너뛰기
            
            for row in csv_data:
                try:
                    category, item_name, description, quantity1, spec1, quantity2, spec2, unit_price, total_price, assigned_amount = row
                    add_project_item(
                        selected_project_id,
                        category,
                        item_name,
                        description,
                        int(quantity1) if quantity1 and quantity1 != '-' else 0,
                        spec1,
                        int(quantity2) if quantity2 and quantity2 != '-' else 0,
                        spec2,
                        float(unit_price.replace(',', '').strip()) if unit_price and unit_price != '-' else 0,
                        float(total_price.replace(',', '').strip()) if total_price and total_price != '-' else 0,
                        float(assigned_amount.replace(',', '').strip()) if assigned_amount and assigned_amount != '-' else 0
                    )
                    st.success(f"항목 '{item_name}'이(가) 추가되었습니다.")
                except Exception as e:
                    st.error(f"항목 '{item_name}' 추가 중 오류 발생: {str(e)}")
            
            # 프로젝트 예산 정보 업데이트
            update_project_budget(selected_project_id)
            st.success("모든 항목이 처리되었으며, 프로젝트 예산 정보가 업데이트되었습니다.")
    else:
        st.warning("프로젝트를 먼저 선택해주세요.")

def main():
    st.title("프로젝트 관리 시스템")
    
    display_projects()
    
    menu = st.sidebar.selectbox("메뉴 선택", [MENU_PROJECT_ADD, MENU_PROJECT_ITEM_ADD, MENU_EXPENDITURE_REQUEST, MENU_EXPENDITURE_APPROVE, MENU_PROJECT_DETAIL, MENU_BULK_IMPORT, "프로젝트 항목 대량 추가"])

    if menu == MENU_PROJECT_ADD:
        add_project_menu()
    elif menu == MENU_PROJECT_ITEM_ADD:
        add_project_item_menu()
    elif menu == MENU_EXPENDITURE_REQUEST:
        request_expenditure_menu()
    elif menu == MENU_EXPENDITURE_APPROVE:
        approve_expenditure_menu()
    elif menu == MENU_PROJECT_DETAIL:
        project_detail_menu()
    elif menu == MENU_BULK_IMPORT:
        bulk_import_menu()
    elif menu == "프로젝트 항목 대량 추가":
        bulk_import_project_items_menu()

if __name__ == "__main__":
    setup_database()
    main()