import os
from io import BytesIO

import pandas as pd
import openpyxl
import streamlit as st
from streamlit_option_menu import option_menu
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

import openai

# Load environment variables from .env file
load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

if not client:
    st.error("OpenAI API key not found. Please set it in the .env file.")

# Database connection setup
DATABASE = os.path.join(os.getcwd(), 'budget.db')
engine = create_engine(f'sqlite:///{DATABASE}')

def create_tables():
    try:
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS budget_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    대분류 TEXT,
                    항목명 TEXT,
                    단가 INTEGER,
                    개수1 INTEGER,
                    단위1 TEXT,
                    개수2 INTEGER,
                    단위2 TEXT,
                    배정예산 INTEGER
                )
            """))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    budget_item_id INTEGER,
                    지출금액 INTEGER,
                    지출일자 DATE,
                    협력사 TEXT,
                    FOREIGN KEY (budget_item_id) REFERENCES budget_items (id)
                )
            """))
            conn.commit()
    except Exception as e:
        st.error(f"An error occurred while creating tables: {e}")

def get_existing_budget_data():
    with engine.connect() as conn:
        df = pd.read_sql_query(text("SELECT * FROM budget_items"), conn)
    return df

def update_database(df):
    with engine.connect() as conn:
        df.to_sql('budget_items', conn, if_exists='replace', index=False)

def budget_input():
    st.subheader("예산 항목 입력")
    
    df = get_existing_budget_data()
    
    if df.empty:
        df = pd.DataFrame(columns=['대분류', '항목명', '단가', '개수1', '단위1', '개수2', '단위2'])
    
    existing_categories = list(df['대분류'].unique())
    new_category = st.text_input("새 대분류 이름 (기존 대분류 수정 또는 새로 추가)")
    all_categories = existing_categories + ([new_category] if new_category and new_category not in existing_categories else [])
    selected_category = st.selectbox("대분류 선택", options=all_categories)
    
    category_df = df[df['대분류'] == selected_category] if selected_category in existing_categories else pd.DataFrame(columns=df.columns)
    
    edited_df = st.data_editor(
        category_df,
        column_config={
            "항목명": st.column_config.TextColumn(required=True, width="large"),
            "단가": st.column_config.NumberColumn(required=True, min_value=0, width="medium", format="₩%d"),
            "개수1": st.column_config.NumberColumn(required=True, min_value=1, step=1, width="small"),
            "단위1": st.column_config.TextColumn(required=True, width="small"),
            "개수2": st.column_config.NumberColumn(required=True, min_value=1, step=1, width="small"),
            "단위2": st.column_config.TextColumn(required=True, width="small"),
        },
        hide_index=True,
        num_rows="dynamic",
        key=f"budget_editor_{selected_category}"
    )
    
    edited_df['대분류'] = selected_category
    edited_df['배정예산'] = (edited_df['단가'] * edited_df['개수1'] * edited_df['개수2']).astype(int)
    
    if st.button("저장"):
        df = df[df['대분류'] != selected_category]
        df = pd.concat([df, edited_df], ignore_index=True)
        update_database(df)
        st.success("데이터가 성공적으로 저장되었습니다.")
    
    st.subheader("전체 예산 항목")
    st.data_editor(
        df,
        column_config={
            "대분류": st.column_config.TextColumn(required=True, width="medium"),
            "항목명": st.column_config.TextColumn(required=True, width="large"),
            "단가": st.column_config.NumberColumn(required=True, min_value=0, width="medium", format="₩%d"),
            "개수1": st.column_config.NumberColumn(required=True, min_value=1, step=1, width="small"),
            "단위1": st.column_config.TextColumn(required=True, width="small"),
            "개수2": st.column_config.NumberColumn(required=True, min_value=1, step=1, width="small"),
            "단위2": st.column_config.TextColumn(required=True, width="small"),
            "배정예산": st.column_config.NumberColumn(required=True, format="₩%d", width="medium", disabled=True),
            "잔액": st.column_config.NumberColumn(required=True, format="₩%d", width="medium", disabled=True),
            "협력사별지출금액_1": st.column_config.NumberColumn(min_value=0, format="₩%d", width="medium"),
            "협력사별지출금액_2": st.column_config.NumberColumn(min_value=0, format="₩%d", width="medium"),
            "협력사별지출금액_3": st.column_config.NumberColumn(min_value=0, format="₩%d", width="medium"),
        },
        hide_index=True,
        use_container_width=True,
        disabled=["배정예산", "잔액"],
        key="updated_budget_editor"
    )

def add_expense():
    st.subheader("지출 추가")
    
    with engine.connect() as conn:
        budget_items = pd.read_sql_query(text("SELECT * FROM budget_items"), conn)
    
    selected_item = st.selectbox("항목 선택", options=budget_items['항목명'].tolist())
    expense_amount = st.number_input("지출 금액", min_value=0, step=1000)
    expense_date = st.date_input("지출 일자")
    partner = st.text_input("협력사")
    
    if st.button("지출 추가"):
        item_id = budget_items[budget_items['항목명'] == selected_item]['id'].values[0]
        
        try:
            with engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO expenses (budget_item_id, 지출금액, 지출일자, 협력사)
                    VALUES (:item_id, :amount, :date, :partner)
                """), {"item_id": item_id, "amount": expense_amount, "date": expense_date, "partner": partner})
                conn.commit()
            
            st.success("지출이 추가되었습니다.")
        except Exception as e:
            st.error(f"An error occurred while adding expense: {e}")

def view_budget():
    st.subheader("예산 및 지출 현황")
    
    with engine.connect() as conn:
        df = pd.read_sql_query(text("""
            SELECT bi.*, COALESCE(SUM(e.지출금액), 0) as 총지출액,
                   bi.배정예산 - COALESCE(SUM(e.지출금액), 0) as 잔액
            FROM budget_items bi
            LEFT JOIN expenses e ON bi.id = e.budget_item_id
            GROUP BY bi.id
        """), conn)
    
    st.dataframe(df)

def analyze_excel(df):
    df_str = df.to_string()
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Analyze this Excel data and convert it to the format with columns: 대분류, 항목명, 단가, 개수1, 단위1, 개수2, 단위2, 배정예산. Here's the data:\n\n{df_str}"}
        ],
        max_tokens=4000
    )
    
    converted_data = response.choices[0].message.content.strip()
    
    try:
        # CSV 문자열을 StringIO 객체로 변환
        csv_data = StringIO(converted_data)
        # 헤더 없이 CSV 파일 읽기
        converted_df = pd.read_csv(csv_data, header=None, names=['대분류', '항목명', '단가', '개수1', '단위1', '개수2', '단위2', '배정예산'])
    except Exception as e:
        st.error(f"데이터 변환 중 오류 발생: {e}")
        st.text("API 응답:")
        st.text(converted_data)
        return None
    
    return converted_df

def upload_excel():
    st.subheader("엑셀 파일 업로드")
    
    uploaded_file = st.file_uploader("엑셀 파일을 선택하세요", type=["xlsx", "xls"])
    
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        st.write("원본 데이터:")
        st.dataframe(df)
        
        if st.button("데이터 분석 및 변환"):
            try:
                converted_df = analyze_excel(df)
                st.write("변환된 데이터:")
                st.dataframe(converted_df)
                
                if st.button("데이터베이스에 저장"):
                    with engine.connect() as conn:
                        converted_df.to_sql('budget_items', conn, if_exists='append', index=False)
                    st.success("데이터가 성공적으로 저장되었습니다.")
            except Exception as e:
                st.error(f"An error occurred during analysis: {e}")

def main():
    create_tables()
    st.title('예산 관리 시스템')
    
    with st.sidebar:
        selected = option_menu("메뉴", ["예산 입력", "지출 추가", "예산 조회", "엑셀 업로드"], 
            icons=['pencil-fill', 'cash-coin', 'eye-fill', 'file-earmark-excel'], menu_icon="list", default_index=0)


    if selected == "예산 입력":
        budget_input()
    elif selected == "지출 추가":
        add_expense()
    elif selected == "예산 조회":
        view_budget()
    elif selected == "엑셀 업로드":
        upload_excel()

if __name__ == '__main__':
    main()