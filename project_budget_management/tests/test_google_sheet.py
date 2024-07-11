import unittest
from unittest.mock import patch
from google_sheet import read_google_sheet

class TestGoogleSheet(unittest.TestCase):
    @patch('google_sheet.get_google_sheet_service')
    def test_read_google_sheet(self, mock_service):
        mock_service.return_value.spreadsheets().values().get().execute.return_value = {'values': [['test']]}
        values = read_google_sheet('dummy_id', 'dummy_range')
        self.assertEqual(values, [['test']])

if __name__ == '__main__':
    unittest.main()