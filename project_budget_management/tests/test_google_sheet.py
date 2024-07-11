import unittest
from google_sheet import read_google_sheet

class TestGoogleSheet(unittest.TestCase):
    def test_read_google_sheet(self):
        sheet_id = 'your_google_sheet_id'
        range_name = 'Sheet1!A1:Z1000'
        values = read_google_sheet(sheet_id, range_name)
        self.assertIsInstance(values, list)

if __name__ == '__main__':
    unittest.main()
