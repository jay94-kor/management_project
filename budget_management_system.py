import streamlit as st
import pandas as pd
import sqlite3

# 데이터베이스 연결 함수
def get_db_connection():
    conn = sqlite3.connect('budget_management.db')
    return conn

# 엑셀 데이터 로드 함수
def load_excel_data(uploaded_file):
    df = pd.read_excel(uploaded_file, sheet_name='예산배정 및 정산서')
    return df

# 데이터베이스에 데이터 삽입 함수
def insert_data_to_db(df):
    conn = get_db_connection()
    cursor = conn.cursor()
    for index, row in df.iterrows():
        cursor.execute('INSERT INTO budget_items (project_name, category, item, description, allocated_amount, used_amount, remaining_amount, company_name) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                       (row['project_name'], row['category'], row['item'], row['description'], row['allocated_amount'], row['used_amount'], row['remaining_amount'], row['company_name']))
    conn.commit()
    conn.close()

# 잔액 계산 함수
def calculate_remaining_amount(allocated, used):
    return allocated - used

# 로그인 함수
def login(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

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
    df = load_excel_data(uploaded_file)
    
    # 데이터프레임의 열 이름 출력
    st.write("엑셀 파일의 열 이름:")
    st.write(df.columns.tolist())
    
    # 고정 칼럼과 자유 작성 칼럼 구분
    fixed_columns = ['project_name', 'category', 'item', 'description', 'allocated_amount']
    available_columns = [col for col in df.columns if col in fixed_columns]
    editable_columns = [col for col in df.columns if col not in fixed_columns]

    # 고정 칼럼 데이터프레임
    if available_columns:
        fixed_df = df[available_columns]
        st.write("고정된 데이터:")
        st.dataframe(fixed_df)
    else:
        st.warning("고정 열을 찾을 수 없습니다. 엑셀 파일의 구조를 확인해주세요.")

    # 자유 작성 칼럼 데이터프레임
    if editable_columns:
        editable_df = df[editable_columns]
        st.write("자유롭게 작성할 데이터:")
        edited_df = st.experimental_data_editor(editable_df)
    else:
        st.warning("편집 가능한 열을 찾을 수 없습니다.")

    # 사용자 정보 입력
    st.write("지출 요청자 정보 입력:")
    requester_name = st.text_input("이름")
    requester_email = st.text_input("이메일")
    requester_phone = st.text_input("전화번호")

    # 데이터 저장 버튼
    if st.button('데이터베이스에 저장'):
        for index, row in edited_df.iterrows():
            df.at[index, 'used_amount'] = row['used_amount']
            df.at[index, 'company_name'] = row['company_name']
            df.at[index, 'remaining_amount'] = calculate_remaining_amount(df.at[index, 'allocated_amount'], row['used_amount'])
        
        insert_data_to_db(df)
        conn = get_db_connection()
        cursor = conn.cursor()
        for index, row in edited_df.iterrows():
            cursor.execute('INSERT INTO payments (budget_item_id, amount, date, requester_name, requester_email, requester_phone) VALUES (?, ?, date("now"), ?, ?, ?)',
                           (index + 1, row['used_amount'], requester_name, requester_email, requester_phone))
        conn.commit()
        conn.close()
        st.success('데이터가 성공적으로 입력되었습니다.')

    # 초과 지출 처리
    def handle_over_budget(project_name, amount):
        st.write(f"프로젝트 '{project_name}'에서 초과 지출이 발생했습니다. 초과 금액: {amount}")
        conn = get_db_connection()
        other_projects = pd.read_sql_query("SELECT DISTINCT project_name FROM budget_items WHERE project_name != ?", conn, params=(project_name,))
        conn.close()
        selected_project = st.selectbox("초과 금액을 충당할 다른 프로젝트를 선택하세요", other_projects['project_name'].tolist())
        if selected_project:
            conn = get_db_connection()
            selected_items = pd.read_sql_query("SELECT item FROM budget_items WHERE project_name = ?", conn, params=(selected_project,))
            conn.close()
            selected_item = st.selectbox("항목을 선택하세요", selected_items['item'].tolist())
            if st.button('충당'):
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('UPDATE budget_items SET remaining_amount = remaining_amount - ? WHERE project_name = ? AND item = ?', (amount, selected_project, selected_item))
                cursor.execute('UPDATE budget_items SET remaining_amount = remaining_amount + ? WHERE project_name = ? AND item = ?', (amount, project_name, selected_item))
                conn.commit()
                conn.close()
                st.success(f"프로젝트 '{selected_project}'의 항목 '{selected_item}'에서 초과 금액을 충당했습니다.")

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