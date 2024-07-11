import unittest
from flask import Flask
from dashboard import create_dashboard

class TestDashboard(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        create_dashboard(self.app)
        self.client = self.app.test_client()

    def test_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
