import os
from io import BytesIO, StringIO
import json
import re
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
            {"role": "system", "content": "당신은 복잡한 엑셀 데이터를 분석하고 구조화하는 전문가입니다."},
            {"role": "user", "content": f"""
            다음 엑셀 데이터를 분석하고 '대분류', '항목명', '단가', '개수1', '단위1', '개수2', '단위2', '배정예산' 열을 가진 JSON 배열 형식으로 변환해주세요.
            이 엑셀 파일의 구조는 다음과 같습니다:
            1. 상단에는 제목이나 기본 정보가 있을 수 있습니다.
            2. 실제 예산 정보는 파일의 하단 부분에 있습니다.
            3. 병합된 셀이 많으며, 트리 구조로 되어 있을 수 있습니다.

            다음 지침을 따라주세요:
            1. 상단의 제목이나 기본 정보는 무시하고, 실제 예산 데이터만 추출하세요.
            2. 병합된 셀의 값은 하위 항목에 대해 반복되어야 합니다.
            3. 빈 셀이나 소계, 합계 행은 제외하고 실제 데이터만 포함해주세요.
            4. 숫자 데이터는 정수형으로 변환해주세요.
            5. 열 이름이 정확히 일치하지 않을 수 있으므로, 의미가 유사한 열을 찾아 매핑해주세요.
            6. 데이터의 계층 구조를 파악하여 '대분류'와 '항목명'을 적절히 채워주세요.
            7. JSON 배열 형식으로만 응답해주세요. 다른 설명은 필요 없습니다.

            {df_str}
            """}
        ]
    )
    
    try:
        content = response.choices[0].message.content.strip()
        # JSON 시작과 끝 부분 찾기
        start = content.find('[')
        end = content.rfind(']') + 1
        if start != -1 and end != -1:
            json_str = content[start:end]
            structured_data = json.loads(json_str)
            return pd.DataFrame(structured_data)
        else:
            raise ValueError("유효한 JSON 데이터를 찾을 수 없습니다.")
    except json.JSONDecodeError as e:
        st.error(f"GPT 응답을 JSON으로 파싱하는 데 실패했습니다: {str(e)}")
        st.text("GPT 응답:")
        st.text(response.choices[0].message.content)
    except ValueError as e:
        st.error(str(e))
        st.text("GPT 응답:")
        st.text(response.choices[0].message.content)
    except Exception as e:
        st.error(f"예상치 못한 오류가 발생했습니다: {str(e)}")
        st.text("GPT 응답:")
        st.text(response.choices[0].message.content)
    return None

def upload_excel():
    st.subheader("엑셀 파일 업로드")
    
    uploaded_file = st.file_uploader("엑셀 파일을 선택하세요", type=["xlsx", "xls"])
    
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file, header=None)  # header=None으로 모든 행을 데이터로 읽음
            st.write("원본 데이터:")
            st.dataframe(df)
            
            converted_df = analyze_excel(df)
            if converted_df is not None:
                st.write("변환된 데이터:")
                st.dataframe(converted_df)
                
                if st.button("데이터베이스에 저장"):
                    with engine.connect() as conn:
                        converted_df.to_sql('budget_items', conn, if_exists='append', index=False)
                    st.success("데이터가 성공적으로 저장되었습니다.")
        except Exception as e:
            st.error(f"파일 처리 중 오류 발생: {str(e)}")
            st.text("오류 상세:")
            st.text(str(e))

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