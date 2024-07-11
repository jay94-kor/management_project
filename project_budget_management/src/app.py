import streamlit as st
from dashboard import create_dashboard

def main():
    st.title("프로젝트 예산 관리 대시보드")
    create_dashboard()

if __name__ == '__main__':
    main()