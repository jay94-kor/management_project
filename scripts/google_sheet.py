import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_google_sheet(sheet_id):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials/service_account.json', scope)  # 경로 수정
    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_id).sheet1
    return sheet

# 예시 사용법
if __name__ == "__main__":
    sheet_id = "16MdrQJghAOhA4XTdDqLaHHf5IuSx5iGe"
    sheet = get_google_sheet(sheet_id)
    print(sheet.get_all_records())