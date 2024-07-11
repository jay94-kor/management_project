import unittest
from app.utils import log_action, get_logs
from app.db import create_connection

class TestUtils(unittest.TestCase):
    def setUp(self):
        self.conn = create_connection(":memory:")
        self.create_test_data()

    def create_test_data(self):
        cur = self.conn.cursor()
        cur.execute("CREATE TABLE logs (id integer PRIMARY KEY, project_id integer, action text, timestamp text, details text)")
        self.conn.commit()

    def test_log_action(self):
        log_action(self.conn, 1, 'test_action', 'test_details')
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM logs")
        rows = cur.fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][2], 'test_action')
        self.assertEqual(rows[0][3], 'test_details')

    def test_get_logs(self):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO logs (project_id, action, timestamp, details) VALUES (1, 'test_action', '2023-01-01 00:00:00', 'test_details')")
        self.conn.commit()
        logs = get_logs(self.conn)
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0][2], 'test_action')

if __name__ == '__main__':
    unittest.main()
