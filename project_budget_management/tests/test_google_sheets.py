import unittest
from app.google_sheets import authenticate_google_sheets

class TestGoogleSheets(unittest.TestCase):
    def test_authenticate_google_sheets(self):
        # Test will fail without valid credentials
        self.assertRaises(Exception, authenticate_google_sheets, 'invalid_credentials.json')

if __name__ == '__main__':
    unittest.main()
