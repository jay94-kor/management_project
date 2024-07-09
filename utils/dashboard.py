import streamlit as st
import pandas as pd
import plotly.express as px

def create_dashboard(data):
    df = pd.DataFrame(data, columns=['category', 'subcategory', 'amount'])
    
    # 총 예산
    total_budget = df['amount'].sum()
    st.metric("총 예산", f"${total_budget:,.2f}")

    # 카테고리별 예산 분포
    fig = px.pie(df, values='amount', names='category', title='카테고리별 예산 분포')
    st.plotly_chart(fig)

    # 서브카테고리별 예산 분포 (상위 10개)
    subcategory_budget = df.groupby('subcategory')['amount'].sum().sort_values(ascending=False).head(10)
    fig = px.bar(subcategory_budget, x=subcategory_budget.index, y='amount', title='상위 10개 서브카테고리 예산')
    st.plotly_chart(fig)

    # 예산 사용 현황 (예시 - 실제 데이터는 구글 시트에서 가져와야 함)
    st.subheader("예산 사용 현황")
    usage_data = {
        'category': ['A', 'B', 'C', 'D'],
        'budget': [1000, 2000, 1500, 3000],
        'used': [800, 1600, 1200, 2700]
    }
    usage_df = pd.DataFrame(usage_data)
    usage_df['remaining'] = usage_df['budget'] - usage_df['used']
    fig = px.bar(usage_df, x='category', y=['used', 'remaining'], title='카테고리별 예산 사용 현황')
    st.plotly_chart(fig)