from sqlalchemy.orm import Session
from database import Project, Transaction, SessionLocal

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

def add_project(name, assigned_budget):
    with get_session() as session:
        project = Project(name=name, assigned_budget=assigned_budget, remaining_budget=assigned_budget)
        session.add(project)

def record_transaction(project_id, description, amount, date):
    with get_session() as session:
        transaction = Transaction(project_id=project_id, description=description, amount=amount, date=date)
        project = session.query(Project).filter(Project.id == project_id).first()
        project.spent_budget += amount
        project.remaining_budget -= amount
        session.add(transaction)

def get_project_budget(project_id):
    with get_session() as session:
        project = session.query(Project).filter(Project.id == project_id).first()
        return {
            'assigned_budget': project.assigned_budget,
            'spent_budget': project.spent_budget,
            'remaining_budget': project.remaining_budget
        }