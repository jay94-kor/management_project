import unittest
from database import init_db, SessionLocal, Project

class TestDatabase(unittest.TestCase):
    def setUp(self):
        init_db()
        self.session = SessionLocal()

    def tearDown(self):
        self.session.close()

    def test_add_project(self):
        project = Project(name="Test Project", assigned_budget=1000, remaining_budget=1000)
        self.session.add(project)
        self.session.commit()
        fetched_project = self.session.query(Project).filter_by(name="Test Project").first()
        self.assertEqual(fetched_project.assigned_budget, 1000)

if __name__ == '__main__':
    unittest.main()
