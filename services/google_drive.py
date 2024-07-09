import asyncio
import logging
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import streamlit as st
import json
import openpyxl
import io
from googleapiclient.http import MediaIoBaseDownload
import httplib2
import ssl

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Google Drive API 설정
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_INFO = json.loads(st.secrets["gcp_service_account"]["service_account_info"])

creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/drive.readonly'])
service = build('drive', 'v3', credentials=creds, cache_discovery=False)

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

def get_project_list(folder_id):
    files = list_files_in_folder(folder_id)
    projects = []
    for file in files:
        file_id = file['id']
        file_name = file['name']
        
        # SSL 검증을 비활성화한 HTTP 객체 생성
        http = httplib2.Http(disable_ssl_certificate_validation=True)

        # 파일 다운로드
        request = service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk(num_retries=2)
        
        # 엑셀 파일 열기
        fh.seek(0)
        wb = openpyxl.load_workbook(fh)
        sheet = wb.active
        
        # 필요한 데이터 추출
        project_name = sheet['D3'].value
        client_name = sheet['G3'].value
        author_affiliation = sheet['D4'].value
        creation_date = sheet['E4'].value
        event_date = sheet['J4'].value
        event_location = sheet['J3'].value
        contract_start_date = sheet['M3'].value
        contract_end_date = sheet['M4'].value
        
        # 카테고리, 항목, 내용, 배정금액 추출
        categories = []
        items = []
        descriptions = []
        allocated_amounts = []
        row = 8
        while sheet[f'B{row}'].value:
            category = sheet[f'B{row}'].value
            if '내부인건비' not in category:
                categories.append(category)
                items.append(sheet[f'C{row}'].value)
                descriptions.append(sheet[f'D{row}'].value)
                allocated_amounts.append(sheet[f'L{row}'].value)
            row += 1
        
        projects.append({
            'id': file_id,
            'name': project_name,
            'client': client_name,
            'author_affiliation': author_affiliation,
            'creation_date': creation_date,
            'event_date': event_date,
            'event_location': event_location,
            'contract_start_date': contract_start_date,
            'contract_end_date': contract_end_date
        })
    return projects

def list_files_in_folder(folder_id):
    try:
        results = service.files().list(q=f"'{folder_id}' in parents", pageSize=10, fields="files(id, name)").execute()
        return results.get('files', [])
    except Exception as e:
        print(f"Error listing files: {e}")
        return []