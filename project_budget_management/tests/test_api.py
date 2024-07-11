import unittest
from app.api import transfer_budget_item, transfer_budget_project
from app.db import create_connection

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.conn = create_connection(":memory:")
        self.create_test_data()

    def create_test_data(self):
        cur = self.conn.cursor()
        cur.execute("CREATE TABLE budget_items (id integer PRIMARY KEY, project_id integer, allocated_budget real, actual_cost real)")
        cur.execute("INSERT INTO budget_items (id, project_id, allocated_budget, actual_cost) VALUES (1, 1, 1000, 500)")
        cur.execute("INSERT INTO budget_items (id, project_id, allocated_budget, actual_cost) VALUES (2, 1, 1000, 500)")
        self.conn.commit()

    def test_transfer_budget_item(self):
        result = transfer_budget_item(self.conn, 1, 2, 200)
        self.assertTrue(result)
        cur = self.conn.cursor()
        cur.execute("SELECT allocated_budget FROM budget_items WHERE id=1")
        from_budget = cur.fetchone()[0]
        cur.execute("SELECT allocated_budget FROM budget_items WHERE id=2")
        to_budget = cur.fetchone()[0]
        self.assertEqual(from_budget, 800)
        self.assertEqual(to_budget, 1200)

    def test_transfer_budget_project(self):
        cur = self.conn.cursor()
        cur.execute("CREATE TABLE projects (id integer PRIMARY KEY, name text NOT NULL)")
        cur.execute("INSERT INTO projects (id, name) VALUES (1, 'Project 1')")
        cur.execute("INSERT INTO projects (id, name) VALUES (2, 'Project 2')")
        cur.execute("INSERT INTO budget_items (id, project_id, allocated_budget, actual_cost) VALUES (3, 2, 500, 300)")
        result = transfer_budget_project(self.conn, 1, 2, 200)
        self.assertTrue(result)
        cur.execute("SELECT SUM(allocated_budget - actual_cost) FROM budget_items WHERE project_id=1")
        from_project_budget = cur.fetchone()[0]
        cur.execute("SELECT SUM(allocated_budget - actual_cost) FROM budget_items WHERE project_id=2")
        to_project_budget = cur.fetchone()[0]
        self.assertEqual(from_project_budget, 800)
        self.assertEqual(to_project_budget, 400)

if __name__ == '__main__':
    unittest.main()
