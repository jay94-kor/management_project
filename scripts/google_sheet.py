import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_google_sheet(sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('path_to_credentials.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).sheet1
    return sheet

# 예시 사용법
if __name__ == "__main__":
    sheet = get_google_sheet("예산 배정 및 정산서")
    print(sheet.get_all_records())
