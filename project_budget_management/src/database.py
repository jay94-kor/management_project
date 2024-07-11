import matplotlib.pyplot as plt
import io
import base64
from flask import Flask, render_template
from sqlalchemy.orm import Session
from database import Project, SessionLocal
from contextlib import contextmanager

@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

def create_dashboard(app):
    @app.route('/')
    def index():
        with get_session() as session:
            projects = session.query(Project).all()
        
        # 차트 생성
        project_names = [project.name for project in projects]
        spent_budgets = [project.spent_budget for project in projects]
        assigned_budgets = [project.assigned_budget for project in projects]

        fig, ax = plt.subplots()
        ax.pie(spent_budgets, labels=project_names, autopct='%1.1f%%')
        ax.axis('equal')

        # 차트를 이미지로 변환
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        chart_url = base64.b64encode(img.getvalue()).decode()

        return render_template('dashboard.html', projects=projects, chart_url=chart_url)