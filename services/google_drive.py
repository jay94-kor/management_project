import asyncio
import logging
from googleapiclient.discovery import build
from google.oauth2 import service_account
import streamlit as st
import json
import openpyxl
import io
from googleapiclient.http import MediaIoBaseDownload

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

async def get_project_list(folder_id):
    files = await list_files_in_folder(folder_id)
    projects = []
    for file in files:
        file_id = file['id']
        file_name = file['name']
        
        # 파일 다운로드
        request = service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        
        # 엑셀 파일 열기
        fh.seek(0)
        wb = openpyxl.load_workbook(fh)
        parts = file['name'].split('_')
        affiliation = parts[1].strip()
        project_name = parts[2].strip()
        projects.append({
            'id': file['id'],
            'affiliation': affiliation,
            'name': project_name
        })
    return projects