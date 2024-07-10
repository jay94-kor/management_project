import streamlit as st
from pages.home import home_page
from pages.project import project_page
from pages.budget import budget_page

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Project Management", "Budget Management"])

if page == "Home":
    home_page()
elif page == "Project Management":
    project_page()
elif page == "Budget Management":
    budget_page()
