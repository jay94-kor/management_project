import streamlit as st
import pandas as pd
import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from components.db import get_db_connection

# 초기 데이터 설정 및 스트림릿 앱 실행
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        '프로젝트명': [],
        '구분': [],
        '예산과목': [],
        '항목': [],
        '내용': [],
        '수량': [],
        '규격': [],
        '일수': [],
        '일수 규격': [],
        '회': [],
        '회 규격': [],
        '단가': [],
        '배정 금액': [],
        '수주금액': []
    })

# 프로젝트명 선택
selected_project = st.selectbox('프로젝트명 선택', st.session_state.data['프로젝트명'].unique())

# 선택한 프로젝트의 데이터 필터링
project_data = st.session_state.data[st.session_state.data['프로젝트명'] == selected_project]

# 데이터프레임 표시
st.dataframe(project_data)

# 입력 폼 작성
with st.form(key='update_form'):
    구분 = st.text_input('구분')
    예산과목 = st.text_input('예산과목')
    항목 = st.text_input('항목')
    내용 = st.text_input('내용')
    수량 = st.number_input('수량', min_value=0)
    규격 = st.text_input('규격')
    일수 = st.number_input('일수', min_value=0)
    일수_규격 = st.text_input('일수 규격')
    회 = st.number_input('회', min_value=0)
    회_규격 = st.text_input('회 규격')
    단가 = st.number_input('단가', min_value=0)
    배정_금액 = st.number_input('배정 금액', min_value=0)
    수주금액 = st.number_input('수주금액', min_value=0)
    제출 = st.form_submit_button('제출')

    if 제출:
        new_data = {
            '프로젝트명': selected_project,
            '구분': 구분,
            '예산과목': 예산과목,
            '항목': 항목,
            '내용': 내용,
            '수량': 수량,
            '규격': 규격,
            '일수': 일수,
            '일수 규격': 일수_규격,
            '회': 회,
            '회 규격': 회_규격,
            '단가': 단가,
            '배정 금액': 배정_금액,
            '수주금액': 수주금액
        }
        st.session_state.data = st.session_state.data.append(new_data, ignore_index=True)
        st.success('데이터가 추가되었습니다.')

# 업데이트된 데이터프레임 다시 표시
project_data = st.session_state.data[st.session_state.data['프로젝트명'] == selected_project]
st.dataframe(project_data)
