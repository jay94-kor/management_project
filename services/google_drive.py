import streamlit as st
import json
import os
from googleapiclient.discovery import build
from google.oauth2 import service_account
import io
from googleapiclient.http import MediaIoBaseDownload

# Google Drive API 설정
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_INFO = json.loads(st.secrets["gcp_service_account"]["service_account_info"])

credentials = service_account.Credentials.from_service_account_info(
    SERVICE_ACCOUNT_INFO, scopes=SCOPES)
service = build('drive', 'v3', credentials=credentials)

def list_files_in_folder(folder_id):
    """Google Drive 폴더 내의 파일 목록을 반환합니다."""
    query = f"'{folder_id}' in parents and mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'"
    results = service.files().list(q=query, pageSize=10, fields="files(id, name)").execute()
    items = results.get('files', [])
    return items

def download_file(file_id, file_name):
    """Google Drive에서 파일을 다운로드합니다."""
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(file_name, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    return file_name

def convert_xlsx_to_sheet(file_id):
    """엑셀 파일을 Google Sheets로 변환하고 스프레드시트 ID를 반환합니다."""
    file_metadata = {
        'name': 'ConvertedSpreadsheet',
        'mimeType': 'application/vnd.google-apps.spreadsheet'
    }
    file = service.files().copy(
        fileId=file_id,
        body=file_metadata,
        fields='id'
    ).execute()
    return file.get('id')

def monitor_and_convert(folder_id):
    """Google Drive 폴더를 모니터링하고 새로운 엑셀 파일을 Google Sheets로 변환합니다."""
    files = list_files_in_folder(folder_id)
    if files:
        for file in files:
            print(f"Found file: {file['name']} (ID: {file['id']})")
            spreadsheet_id = convert_xlsx_to_sheet(file['id'])
            print(f"Converted to Google Sheets: {spreadsheet_id}")
            return spreadsheet_id
    else:
        print("No files found.")
        return None