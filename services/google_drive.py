import asyncio
import logging
from googleapiclient.discovery import build
from google.oauth2 import service_account
import streamlit as st
import json

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Google Drive API 설정
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_INFO = json.loads(st.secrets["gcp_service_account"]["service_account_info"])

credentials = service_account.Credentials.from_service_account_info(
    SERVICE_ACCOUNT_INFO, scopes=SCOPES)
service = build('drive', 'v3', credentials=credentials)

async def list_files_in_folder(folder_id):
    query = f"'{folder_id}' in parents and mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'"
    try:
        results = await asyncio.to_thread(
            service.files().list(q=query, pageSize=10, fields="files(id, name)").execute
        )
        return results.get('files', [])
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        return []

async def convert_xlsx_to_sheet(file_id):
    file_metadata = {
        'name': 'ConvertedSpreadsheet',
        'mimeType': 'application/vnd.google-apps.spreadsheet'
    }
    try:
        file = await asyncio.to_thread(
            service.files().copy(fileId=file_id, body=file_metadata, fields='id').execute
        )
        return file.get('id')
    except Exception as e:
        logger.error(f"Error converting file: {e}")
        return None

async def monitor_and_convert(folder_id):
    while True:
        files = await list_files_in_folder(folder_id)
        for file in files:
            logger.info(f"Found file: {file['name']} (ID: {file['id']})")
            spreadsheet_id = await convert_xlsx_to_sheet(file['id'])
            if spreadsheet_id:
                logger.info(f"Converted to Google Sheets: {spreadsheet_id}")
                return spreadsheet_id
        await asyncio.sleep(60)  # 1분마다 확인