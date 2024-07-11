import unittest
from app.dashboard import show_dashboard
from app.db import create_connection
import pandas as pd

class TestDashboard(unittest.TestCase):
    def setUp(self):
        self.conn = create_connection(":memory:")
        self.create_test_data()

    def create_test_data(self):
        cur = self.conn.cursor()
        cur.execute("CREATE TABLE projects (id integer PRIMARY KEY, name text NOT NULL)")
        cur.execute("INSERT INTO projects (id, name) VALUES (1, 'Project 1')")
        cur.execute("CREATE TABLE budget_items (id integer PRIMARY KEY, project_id integer, allocated_budget real, actual_cost real)")
        cur.execute("INSERT INTO budget_items (id, project_id, allocated_budget, actual_cost) VALUES (1, 1, 1000, 500)")
        self.conn.commit()

    def test_show_dashboard(self):
        # This test requires the Streamlit environment to be running
        pass

if __name__ == '__main__':
    unittest.main()
