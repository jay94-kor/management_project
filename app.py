import streamlit as st
import pandas as pd
import sqlite3
from sqlalchemy import create_engine, text
import tempfile
import os
import numpy as np
import uuid
from contextlib import contextmanager
import plotly.express as px

st.set_page_config(layout="wide")

# CSS를 사용하여 전체 글자 크기 조절
st.markdown("""
    <style>
    .reportview-container .main .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-right: 2rem;
        padding-left: 2rem;
        padding-bottom: 2rem;
    }
    @media (max-width: 768px) {
        .reportview-container .main .block-container {
            padding: 1rem;
        }
    }
    html, body, [class*="css"]  {
        font-size: 0.95rem;
    }
    @media (max-width: 768px) {
        html, body, [class*="css"]  {
            font-size: 0.8rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# 상수 정의
DB_PATH = 'sqlite:///project_info.db'
PROJECT_TABLE_PREFIX = 'Project_'
PROJECT_INFO_TABLE_SUFFIX = '_Info'

@contextmanager
def get_db_connection():
    engine = create_engine(DB_PATH, echo=False)
    try:
        with engine.connect() as conn:
            yield conn
    finally:
        engine.dispose()

# Define the extraction functions
def extract_project_info(df):
    project_info = {
        '프로젝트명': df.iloc[1, 3],
        '클라이언트': df.iloc[1, 6],
        '작성자/소속': df.iloc[2, 3],
        '작성일': str(df.iloc[2, 6]),
        '행사장소': df.iloc[1, 9],
        '행사일시': str(df.iloc[2, 9]),
        '계약시작일': str(df.iloc[1, 11]),
        '계약종료일': str(df.iloc[2, 11])
    }
    
    # 날짜 필드에 대해 변환 시도
    date_fields = ['작성일', '행사일시', '계약시작일', '계약종료일']
    for field in date_fields:
        try:
            project_info[field] = pd.to_datetime(project_info[field]).date()
        except:
            # 변환 실패 시 원본 문자열 유지
            pass
    
    return project_info

def extract_budget_settlement(df):
    # 더 넓은 범위의 데이터를 읽어옵니다.
    budget_settlement = df.iloc[6:].copy()  # 6번째 행부터 끝까지 모든 데이터를 읽습니다.
    
    # 실제 열 수 확인
    actual_columns = budget_settlement.columns
    
    # 새로운 열 이름 정의
    new_columns = ['구분', '항목', '내용', '산출내역', 
                   '수량1', '규격1', '수량2', '규격2', 
                   '투입률', '단가', '금액', '예상단가', '예산과목', 
                   '정산금액', '차액', '수익률', '거래업체명', '협력사등록유무', '비고']
    
    # 실제 열 수에 맞게 열 이름 조정
    if len(actual_columns) > len(new_columns):
        additional_columns = [f'추가열_{i+1}' for i in range(len(actual_columns) - len(new_columns))]
        new_columns.extend(additional_columns)
    elif len(actual_columns) < len(new_columns):
        new_columns = new_columns[:len(actual_columns)]
    
    budget_settlement.columns = new_columns
    
    # 통합셀 값 복사
    for col in budget_settlement.columns:
        budget_settlement[col] = budget_settlement[col].fillna(method='ffill')
    
    # '소계' 또는 'vat' 키워드가 포함된 행 삭제 (모든 열에서 검사, 대소문자 구분 없이)
    budget_settlement = budget_settlement[~budget_settlement.apply(lambda row: row.astype.str().str.contains('소계|vat|VAT|간접경비', case=False, regex=True).any(), axis=1)]
    
    # NaN 값만 있는 행 제거
    budget_settlement = budget_settlement.dropna(how='all')
    
    # 숫자 데이터 처리
    numeric_columns = ['수량1', '수량2', '투입률', '단가', '금액', '예상단가', '정산금액', '차액']
    for col in numeric_columns:
        if col in budget_settlement.columns:
            budget_settlement[col] = pd.to_numeric(budget_settlement[col], errors='coerce')
    
    # '예상단가' 열이 0이거나 NaN인 행 삭제
    budget_settlement = budget_settlement[budget_settlement['예상단가'].notna() & (budget_settlement['예상단가'] != 0)]
    
    # 고유 ID 추가
    budget_settlement['id'] = [str(uuid.uuid4()) for _ in range(len(budget_settlement))]
    
    return budget_settlement

def process_files(file_paths, sheet_name):
    project_info_list = []
    budget_settlement_list = []
    for file_path in file_paths:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        project_info = extract_project_info(df)
        budget_settlement = extract_budget_settlement(df)
        project_info_list.append(project_info)
        budget_settlement_list.append(budget_settlement)
    combined_budget_settlement = pd.concat(budget_settlement_list, ignore_index=True)
    return project_info_list, combined_budget_settlement

def create_tables(conn):
    conn.execute(text('''CREATE TABLE IF NOT EXISTS ProjectList
                    (id TEXT PRIMARY KEY, project_code TEXT, project_name TEXT)'''))
    conn.execute(text('''CREATE TABLE IF NOT EXISTS BudgetConsumptionLog
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     project_id TEXT,
                     item_id TEXT,
                     amount REAL,
                     expense_type TEXT,
                     approval_link TEXT,
                     consumption_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                     is_canceled BOOLEAN DEFAULT 0)'''))
    
    # 'is_canceled' 열이 존재하는지 확인
    result = conn.execute(text("PRAGMA table_info(BudgetConsumptionLog)"))
    columns = [row[1] for row in result]  # 튜플의 두 번째 요소가 열 이름입니다.
    if 'is_canceled' not in columns:
        conn.execute(text('''ALTER TABLE BudgetConsumptionLog ADD COLUMN is_canceled BOOLEAN DEFAULT 0'''))
    
    conn.commit()

def save_project_data(project_info, budget_settlement, project_code):
    unique_id = str(uuid.uuid4())
    table_name = f"{PROJECT_TABLE_PREFIX}{unique_id.replace('-', '_')}"
    
    with get_db_connection() as conn:
        create_tables(conn)
        
        # 프로젝트 리스트에 저장
        conn.execute(text("INSERT INTO ProjectList (id, project_code, project_name) VALUES (:id, :code, :name)"),
                     {"id": unique_id, "code": project_code, "name": project_info['프로젝트명']})
        
        # 프로젝트 데이터 저장
        budget_settlement.to_sql(table_name, conn, if_exists='replace', index=False)
        
        # 프로젝트 정보 저장
        project_info_df = pd.DataFrame([project_info])
        project_info_df.to_sql(f"{table_name}{PROJECT_INFO_TABLE_SUFFIX}", conn, if_exists='replace', index=False)
        
        conn.commit()
    
    return unique_id

def process_budget_consumption(budget_settlement):
    # 예산 소진 처리
    budget_settlement['잔여예산'] = budget_settlement['예상단가']
    budget_settlement['소진금액'] = 0
    
    return budget_settlement

def project_registration_page():
    st.title("프로젝트 등록")
    uploaded_files = st.file_uploader("Excel 파일 업로드", accept_multiple_files=True, type=['xlsx'])
    sheet_name = "예산배정 및 정산서"
    
    if uploaded_files:
        temp_dir = tempfile.TemporaryDirectory()
        file_paths = []
        for uploaded_file in uploaded_files:
            temp_file_path = os.path.join(temp_dir.name, uploaded_file.name)
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            file_paths.append(temp_file_path)
        
        project_info_list, combined_budget_settlement = process_files(file_paths, sheet_name)
        
        st.subheader("예산 배정 및 정산 데이터")
        st.dataframe(combined_budget_settlement)
        
        st.subheader("프로젝트 정보")
        for i, info in enumerate(project_info_list, 1):
            st.write(f"프로젝트 {i}:")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**프로젝트명:** {info['프로젝트명']}")
                st.write(f"**클라이언트:** {info['클라이언트']}")
                st.write(f"**작성자/소속:** {info['작성자/소속']}")
                st.write(f"**작성일:** {info['작성일']}")
            with col2:
                st.write(f"**행사장소:** {info['행사장소']}")
                st.write(f"**행사일시:** {info['행사일시']}")
                st.write(f"**계약시작일:** {info['계약시작일']}")
                st.write(f"**계약종료일:** {info['계약종료일']}")
            st.write("---")
        
        project_code = st.text_input("프로젝트 코드 (4글자)", max_chars=4)
        if st.button("데이터베이스에 저장") and project_code:
            if len(project_code) == 4:
                unique_id = save_project_data(project_info_list[0], combined_budget_settlement, project_code)
                st.success(f"데이터가 성공적으로 저장되었습니다. (참조 ID: {unique_id})")
            else:
                st.error("프로젝트 코드는 정확히 4글자여야 합니다.")

def load_project_list():
    with get_db_connection() as conn:
        return pd.read_sql_query("SELECT * FROM ProjectList", conn)

def load_budget_data(project_id):
    with get_db_connection() as conn:
        return pd.read_sql_query(f"SELECT * FROM {PROJECT_TABLE_PREFIX}{project_id.replace('-', '_')}", conn)

def update_budget_data(project_id, budget_data):
    with get_db_connection() as conn:
        budget_data.to_sql(f"{PROJECT_TABLE_PREFIX}{project_id.replace('-', '_')}", conn, if_exists='replace', index=False)

def consume_budget(project_id, budget_data, selected_rows, amount_to_consume, expense_type, approval_link):
    with get_db_connection() as conn:
        with conn.begin():
            remaining_amount = amount_to_consume
            for index, row in selected_rows.iterrows():
                available_budget = int(row['잔여예산'].replace(',', ''))
                if remaining_amount > 0:
                    amount_to_deduct = min(remaining_amount, available_budget)
                    new_remaining_budget = available_budget - amount_to_deduct
                    new_consumed_amount = int(row['소진금액'].replace(',', '')) + amount_to_deduct
                    budget_data.loc[index, '잔여예산'] = f"{new_remaining_budget:,}"
                    budget_data.loc[index, '소진금액'] = f"{new_consumed_amount:,}"
                    remaining_amount -= amount_to_deduct
                    
                    conn.execute(text("""
                        INSERT INTO BudgetConsumptionLog 
                        (project_id, item_id, amount, expense_type, approval_link) 
                        VALUES (:project_id, :item_id, :amount, :expense_type, :approval_link)
                    """), {
                        "project_id": project_id,
                        "item_id": row['id'],
                        "amount": amount_to_deduct,
                        "expense_type": expense_type,
                        "approval_link": approval_link
                    })
            
            update_budget_data(project_id, budget_data)

def budget_execution_page():
    st.title("예산 집행")
    
    projects = load_project_list()
    if projects.empty:
        st.warning("등록된 프로젝트가 없습니다.")
        return
    
    project_options = [f"{row['project_code']}-{row['project_name']}" for _, row in projects.iterrows()]
    selected_project = st.selectbox("프로젝트 선택", project_options)
    
    selected_project_code = selected_project.split('-')[0]
    project_id = projects[projects['project_code'] == selected_project_code]['id'].iloc[0]
    
    budget_data = load_budget_data(project_id)
    
    # '잔여예산'과 '소진금액' 열 추가 또는 초기화
    if '잔여예산' not in budget_data.columns:
        budget_data['잔여예산'] = budget_data['예상단가'].astype(int)
    if '소진금액' not in budget_data.columns:
        budget_data['소진금액'] = 0
    
    # 잔여예산과 소진금액에 3자리마다 콤마 추가
    budget_data['잔여예산'] = budget_data['잔여예산'].apply(lambda x: f"{int(str(x).replace(',', '')):,}")
    budget_data['소진금액'] = budget_data['소진금액'].apply(lambda x: f"{int(str(x).replace(',', '')):,}")
    
    # 체크박스 열 추가
    budget_data['선택'] = False
    
    # 데이터프레임 표시
    columns_to_display = ['선택', '구분', '항목', '산출내역', '잔여예산', '소진금액']
    all_columns = ['id'] + columns_to_display

    # 스타일 적용 함수
    def highlight_columns(s):
        is_remaining_budget = s.name == '잔여예산'
        is_consumed_amount = s.name == '소진금액'
        
        if is_remaining_budget:
            return ['background-color: #e6f3ff' if v != '0' else 'background-color: #cce6ff' for v in s]
        elif is_consumed_amount:
            return ['background-color: #fff0e6' if v != '0' else 'background-color: #ffe6cc' for v in s]
        else:
            return [''] * len(s)

    # 데이터프레임 표시
    edited_df = st.data_editor(
        budget_data[columns_to_display],
        hide_index=True,
        column_config={
            "선택": st.column_config.CheckboxColumn(required=True)
        },
        use_container_width=True,
        height=400
    )

    # 선택된 항목의 총 잔여예산 계산
    selected_rows = edited_df[edited_df['선택']]
    total_available_budget = selected_rows['잔여예산'].apply(lambda x: int(x.replace(',', ''))).sum()
    st.write(f"선택된 항목의 총 잔여예산: {total_available_budget:,}원")
    
    # 전체 프로젝트 예산 계산
    total_budget = int(budget_data['예상단가'].sum())
    total_consumed = int(budget_data['소진금액'].apply(lambda x: int(x.replace(',', ''))).sum())
    total_remaining = total_budget - total_consumed

    # 전체 프로젝트 예산 정보 표시
    st.markdown("<h3 style='font-size: 1.2rem;'>전체 프로젝트 예산 정보</h3>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("총 예산", f"{total_budget:,}원", delta=None, delta_color="off")
    with col2:
        st.metric("소진 예산", f"{total_consumed:,}원", delta=None, delta_color="off")
    with col3:
        st.metric("잔여 예산", f"{total_remaining:,}원", delta=None, delta_color="off")

    # 예산 소진 기능
    st.subheader("예산 소진")
    expense_type = st.selectbox("지출 유형", ["세금계산서", "인건비", "카드", "일반 지출"])
    
    if expense_type == "세금계산서":
        amount_to_consume = st.number_input("소진할 금액 (공급가액)", min_value=0, step=1000, value=0)
        vat_included = st.radio("부가세", ["포함", "별도"])
        if vat_included == "포함":
            total_amount = amount_to_consume
            vat = round(total_amount / 11)
            supply_amount = total_amount - vat
        else:
            supply_amount = amount_to_consume
            vat = round(supply_amount * 0.1)
            total_amount = supply_amount + vat
        st.write(f"공급가액: {int(supply_amount):,}원")
        st.write(f"부가세: {int(vat):,}원")
        st.write(f"합계: {int(total_amount):,}원")
        amount_to_consume = int(supply_amount)  # 부가세 별도 금액만 예산에서 차감
    elif expense_type == "인건비":
        amount_to_consume = st.number_input("이번 회차 합산 금액", min_value=0, step=1000, value=0)
        tax_rate = st.number_input("세율 (%)", min_value=0.0, max_value=100.0, value=3.3, step=0.1)
        tax = round(amount_to_consume * (tax_rate / 100))
        total_amount = amount_to_consume + tax
        st.write(f"소득세: {int(tax):,}원")
        st.write(f"합계: {int(total_amount):,}원")
    else:  # 카드 또는 일반 지출
        amount_to_consume = st.number_input("소진할 금액", min_value=0, step=1000, value=0)
    
    # 모든 지출 유형에 대해 amount_to_consume 설정
    amount_to_consume = int(amount_to_consume)
    
    approval_link = st.text_input("결재서류 링크")
    
    if st.button("예산 소진"):
        if amount_to_consume <= total_available_budget:
            try:
                consume_budget(project_id, budget_data, selected_rows, amount_to_consume, expense_type, approval_link)
                st.success(f"총 {amount_to_consume:,}원의 예산이 소진되었습니다.")
                
                # 업데이트된 예산 데이터 표시 부분 제거
                st.experimental_rerun()  # 페이지를 다시 로드하여 최신 데이터를 표시합니다.
            except Exception as e:
                st.error(f"예산 소진 중 오류가 발생했습니다: {str(e)}")
        else:
            st.error(f"소진할 금액이 선택된 항목의 총 잔여예산을 초과합니다. 최대 {total_available_budget:,}원까지 소진 가능합니다.")

    # 예산 소진 기록 조회
    st.subheader("예산 소진 기록")
    with get_db_connection() as conn:
        consumption_log = pd.read_sql_query(f"""
            SELECT 
                BudgetConsumptionLog.id,
                ProjectList.project_name as 프로젝트명,
                BudgetConsumptionLog.item_id as 항목ID,
                {PROJECT_TABLE_PREFIX}{project_id.replace('-', '_')}.구분,
                {PROJECT_TABLE_PREFIX}{project_id.replace('-', '_')}.항목,
                {PROJECT_TABLE_PREFIX}{project_id.replace('-', '_')}.산출내역,
                BudgetConsumptionLog.amount as 소진금액,
                BudgetConsumptionLog.expense_type as 지출유형,
                BudgetConsumptionLog.approval_link as 결재서류,
                BudgetConsumptionLog.consumption_date as 소진일시,
                BudgetConsumptionLog.is_canceled as 취소여부
            FROM BudgetConsumptionLog 
            JOIN ProjectList ON BudgetConsumptionLog.project_id = ProjectList.id 
            JOIN {PROJECT_TABLE_PREFIX}{project_id.replace('-', '_')} ON BudgetConsumptionLog.item_id = {PROJECT_TABLE_PREFIX}{project_id.replace('-', '_')}.id
            WHERE BudgetConsumptionLog.project_id = '{project_id}'
            ORDER BY consumption_date DESC
        """, conn)

    if not consumption_log.empty:
        # 날짜 형식 변경
        consumption_log['소진일시'] = pd.to_datetime(consumption_log['소진일시']).dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # 금액에 천 단위 구분 기호 추가
        consumption_log['소진금액'] = consumption_log['소진금액'].apply(lambda x: f"{int(x):,}")
        
        # 결재서류 링크를 클릭 가능한 형태로 변경
        consumption_log['결재서류'] = consumption_log['결재서류'].apply(lambda x: f'<a href="{x}" target="_blank">링크</a>' if x else '')
        
        # 표시할 열 선택 (항목ID 제외)
        display_columns = ['프로젝트명', '구분', '항목', '산출내역', '소진금액', '지출유형', '결재서류', '소진일시']
        
        # 데이터프레임 표시
        st.write(consumption_log[display_columns].to_html(escape=False, index=False), unsafe_allow_html=True)

        # 취소 버튼 추가
        for index, row in consumption_log.iterrows():
            if not row['취소여부']:
                if st.button(f"취소 {index}", key=f"cancel_{row['id']}"):
                    with get_db_connection() as conn:
                        # 취소 상태 업데이트
                        conn.execute(text("""
                            UPDATE BudgetConsumptionLog 
                            SET is_canceled = 1 
                            WHERE id = :log_id
                        """), {"log_id": row['id']})

                        # 예산 복구
                        project_table = f"{PROJECT_TABLE_PREFIX}{project_id.replace('-', '_')}"
                        conn.execute(text(f"""
                            UPDATE {project_table}
                            SET 잔여예산 = 잔여예산 + :amount,
                                소진금액 = CASE 
                                    WHEN 소진금액 - :amount < 0 THEN 0
                                    ELSE 소진금액 - :amount
                                END
                            WHERE id = :item_id
                        """), {
                            "amount": int(row['소진금액'].replace(',', '')),
                            "item_id": row['항목ID']
                        })

                        # 취소 기록 추가
                        conn.execute(text("""
                            INSERT INTO BudgetConsumptionLog 
                            (project_id, item_id, amount, expense_type, approval_link, is_canceled) 
                            VALUES (:project_id, :item_id, :amount, '취소', :approval_link, 1)
                        """), {
                            "project_id": project_id,
                            "item_id": row['항목ID'],
                            "amount": int(row['소진금액'].replace(',', '')),
                            "approval_link": f"원본 기록 ID: {row['id']}"
                        })

                        # 취소 후 예산 데이터 다시 불러오기
                        st.experimental_rerun()
    else:
        st.info("아직 예산 소진 기록이 없습니다.")

def project_list_page():
    st.title("프로젝트 목록")
    
    projects = load_project_list()
    
    if projects.empty:
        st.info("등록된 프로젝트가 없습니다.")
    else:
        for _, project in projects.iterrows():
            with st.expander(f"{project['project_code']} - {project['project_name']}"):
                st.write(f"**프로젝트명:** {project['project_name']}")
                st.write(f"**프로젝트 코드:** {project['project_code']}")
                if st.button("상세 정보", key=f"detail_{project['id']}"):
                    show_project_details(project['id'])

    # 선택된 프로젝트의 상세 정보를 표시할 공간
    st.markdown("---")
    st.subheader("프로젝트 상세 정보")
    st.empty()  # 이 공간에 상세 정보가 표시됩니다.

def show_project_details(project_id):
    with get_db_connection() as conn:
        project_info = pd.read_sql_query(f"SELECT * FROM {PROJECT_TABLE_PREFIX}{project_id.replace('-', '_')}{PROJECT_INFO_TABLE_SUFFIX}", conn)
        budget_data = pd.read_sql_query(f"SELECT * FROM {PROJECT_TABLE_PREFIX}{project_id.replace('-', '_')}", conn)
    
    st.markdown("---")
    st.subheader("프로젝트 정보")
    for column in project_info.columns:
        st.write(f"**{column}:** {project_info[column].values[0]}")
    
    st.subheader("예산 정보")
    st.dataframe(budget_data)

def main():
    st.sidebar.title("네비게이션")
    page = st.sidebar.radio("페이지 선택", ["프로젝트 목록", "프로젝트 등록", "예산 집행"])
    
    if page == "프로젝트 목록":
        project_list_page()
    elif page == "프로젝트 등록":
        project_registration_page()
    elif page == "예산 집행":
        budget_execution_page()

if __name__ == "__main__":
    main()
