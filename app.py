import streamlit as st
import pandas as pd
from db.database import get_db_connection, insert_data_to_db
from utils.excel_utils import load_excel_data
from utils.auth import login
from utils.budget_calculations import calculate_remaining_amount, handle_over_budget
from openai import OpenAI
import json
import ast

# Streamlit 앱 레이아웃
st.title('예산 관리 자동화 시스템')

# 로그인 섹션
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def show_login():
    st.write("관리자 로그인")
    username = st.text_input("사용자 이름")
    password = st.text_input("비밀번호", type="password")
    if st.button("로그인"):
        user = login(username, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.user = user
            st.success("로그인 성공!")
            st.experimental_rerun()
        else:
            st.error("사용자 이름 또는 비밀번호가 잘못되었습니다.")

# 상단 우측에 관리자 로그인 버튼
if st.session_state.logged_in:
    st.write(f"환영합니다, {st.session_state.user[1]}")
    if st.button("로그아웃"):
        st.session_state.logged_in = False
        st.experimental_rerun()
else:
    st.sidebar.button("관리자 로그인", on_click=show_login)

# 파일 업로드
uploaded_file = st.file_uploader("엑셀 파일을 업로드 하세요", type="xlsx")

if uploaded_file:
    # OpenAI 클라이언트 초기화
    openai_api_key = st.secrets.get("openai", {}).get("api_key")
    if not openai_api_key:
        st.error("OpenAI API 키가 설정되지 않았습니다. Streamlit 시크릿에 API 키를 추가해주세요.")
    else:
        client = OpenAI(api_key=openai_api_key)

        df = load_excel_data(uploaded_file)
        
        def analyze_and_structure_data(df):
            df_summary = f"Columns: {', '.join(df.columns)}\n"
            df_summary += f"Shape: {df.shape}\n"
            df_summary += f"Sample data:\n{df.head().to_string()}"
            
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",  # GPT-4 대신 GPT-3.5-turbo 사용
                    messages=[
                        {"role": "system", "content": "엑셀 데이터를 분석하고 주어진 DB 구조에 맞게 정리하세요."},
                        {"role": "user", "content": f"다음 엑셀 데이터를 'budget_items' 테이블 구조에 맞게 정리하세요: id, project_name, category, item, description, quantity, specification, input_rate, unit_price, amount, allocated_amount, budget_item, settled_amount, expected_unit_price, ordered_amount, difference, profit_rate, company_name, partner_registered, unregistered_reason, remarks, remaining_amount. 파이썬 딕셔너리 리스트로 반환하세요.\n\n{df_summary}"}
                    ],
                    max_tokens=3000
                )
                
                structured_data = eval(response.choices[0].message.content)
                return structured_data
            except Exception as e:
                st.error(f"OpenAI API 오류: {str(e)}")
                return None

        st.write("데이터 분석 및 구조화 중...")
        structured_data = analyze_and_structure_data(df)

        if structured_data is not None:
            st.write("구조화된 데이터:")
            st.write(structured_data)

            if st.button('데이터베이스에 저장'):
                insert_data_to_db(structured_data)
                st.success('데이터가 성공적으로 데이터베이스에 저장되었습니다.')
        else:
            st.error("데이터 분석 및 구조화 중 오류가 발생했습니다.")

    # 데이터베이스에서 데이터 가져오기
    conn = get_db_connection()
    df_db = pd.read_sql_query("SELECT * FROM budget_items", conn)
    conn.close()

    # 잔액이 음수인 경우 초과 지출 처리
    over_budget = df_db[df_db['remaining_amount'] < 0]
    if not over_budget.empty:
        for index, row in over_budget.iterrows():
            handle_over_budget(row['project_name'], abs(row['remaining_amount']))

    # 데이터베이스에 저장된 데이터 표시
    st.write('데이터베이스에 저장된 예산 항목:')
    st.dataframe(df_db)

    # 수정 요청 및 승인 기능 구현
    if st.session_state.logged_in:
        st.write("수정 요청 및 승인")
        conn = get_db_connection()
        modification_requests = pd.read_sql_query("SELECT * FROM modification_requests WHERE status = 'Pending'", conn)
        conn.close()
        if not modification_requests.empty:
            st.write("승인 대기 중인 수정 요청:")
            st.dataframe(modification_requests)
            selected_request_id = st.selectbox("승인할 수정 요청을 선택하세요", modification_requests['id'].tolist())
            approver_name = st.text_input("승인자 이름")
            if st.button('승인'):
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE modification_requests SET status = 'Approved', approval_date = date('now'), approver_name = ? WHERE id = ?", (approver_name, selected_request_id))
                conn.commit()
                conn.close()
                st.success("수정 요청이 승인되었습니다.")
        else:
            st.write("승인 대기 중인 수정 요청이 없습니다.")

    # 데이터베이스에 저장된 데이터 표시
    st.write('데이터베이스에 저장된 예산 항목:')
    conn = get_db_connection()
    df_db = pd.read_sql_query("SELECT * FROM budget_items", conn)
    conn.close()
    st.dataframe(df_db)