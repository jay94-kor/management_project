import openai
import streamlit as st
import pandas as pd
import plotly.express as px

def classify_data(data):
    openai.api_key = st.secrets["openai"]["api_key"]
    response = openai.Completion.create(
        engine="gpt-4o",
        prompt=f"Classify the following data:\n{data}",
        max_tokens=2500
    )
    return response.choices[0].text.strip()
