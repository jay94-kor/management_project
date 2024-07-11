from flask import Flask, render_template
from sqlalchemy.orm import Session
from database import Project, SessionLocal

def create_dashboard(app):
    @app.route('/')
    def index():
        session = SessionLocal()
        projects = session.query(Project).all()
        session.close()
        return render_template('dashboard.html', projects=projects)
