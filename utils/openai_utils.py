import openai
import streamlit as st

def classify_data(data):
    openai.api_key = st.secrets["openai_api_key"]
    response = openai.Completion.create(
        engine="gpt-4o",
        prompt=f"Classify the following data:\n{data}",
        max_tokens=500
    )
    return response.choices[0].text.strip()
