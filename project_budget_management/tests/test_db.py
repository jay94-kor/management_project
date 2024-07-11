import unittest
from app.db import create_connection

class TestDB(unittest.TestCase):
    def setUp(self):
        self.conn = create_connection(":memory:")

    def test_create_connection(self):
        self.assertIsNotNone(self.conn)

    def test_create_table(self):
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS test (
            id integer PRIMARY KEY,
            name text NOT NULL
        );"""
        cur = self.conn.cursor()
        cur.execute(create_table_sql)
        self.conn.commit()

        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='test';")
        table = cur.fetchone()
        self.assertIsNotNone(table)

if __name__ == '__main__':
    unittest.main()
