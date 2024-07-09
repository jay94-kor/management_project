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

async def get_project_list(folder_id):
    files = await list_files_in_folder(folder_id)
    projects = []
    for file in files:
        project_code, project_name = file['name'].split('_', 1)
        projects.append({
            'id': file['id'],
            'name': project_name,
            'code': project_code
        })
    return projects