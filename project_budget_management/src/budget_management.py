from sqlalchemy.orm import Session
from database import Project, Transaction, SessionLocal

def add_project(name, assigned_budget):
    session = SessionLocal()
    project = Project(name=name, assigned_budget=assigned_budget, remaining_budget=assigned_budget)
    session.add(project)
    session.commit()
    session.close()

def record_transaction(project_id, description, amount, date):
    session = SessionLocal()
    transaction = Transaction(project_id=project_id, description=description, amount=amount, date=date)
    project = session.query(Project).filter(Project.id == project_id).first()
    project.spent_budget += amount
    project.remaining_budget -= amount
    session.add(transaction)
    session.commit()
    session.close()

def get_project_budget(project_id):
    session = SessionLocal()
    project = session.query(Project).filter(Project.id == project_id).first()
    session.close()
    return {
        'assigned_budget': project.assigned_budget,
        'spent_budget': project.spent_budget,
        'remaining_budget': project.remaining_budget
    }
