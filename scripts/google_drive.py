from google.oauth2 import service_account
from googleapiclient.discovery import build
import streamlit as st
from googleapiclient.http import MediaIoBaseUpload
import io
import os
import json

SCOPES = ['https://www.googleapis.com/auth/drive']

def authenticate_drive():
    # 환경 변수에서 서비스 계정 정보 읽기
    service_account_info = json.loads(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON', '{}'))
    
    # Streamlit Secrets에서 읽기 (Streamlit Cloud 사용 시)
    if not service_account_info:
        service_account_info = st.secrets.get("gcp_service_account", {})
    
    if not service_account_info:
        raise ValueError("서비스 계정 정보를 찾을 수 없습니다.")

    print("Service Account Info:", service_account_info.keys())  # 디버깅용

    # service_account_info가 문자열인 경우 JSON으로 파싱
    if isinstance(service_account_info, str):
        service_account_info = json.loads(service_account_info)

    if 'token_uri' not in service_account_info or 'client_email' not in service_account_info:
        raise ValueError("서비스 계정 정보에 필수 필드가 누락되었습니다.")

    creds = service_account.Credentials.from_service_account_info(
        service_account_info,
        scopes=SCOPES
    )
    return build('drive', 'v3', credentials=creds)

def list_drive_files(folder_id):
    service = authenticate_drive()
    query = f"'{folder_id}' in parents and mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'"
    results = service.files().list(q=query, fields="files(id, name, modifiedTime, createdTime)").execute()
    return results.get('files', [])

def get_file_metadata(file_id):
    service = authenticate_drive()
    file = service.files().get(fileId=file_id, fields='name, modifiedTime, createdTime').execute()
    return {
        'title': file['name'],
        'modified_date': file['modifiedTime'],
        'created_date': file['createdTime']
    }

def upload_to_drive(file):
    service = authenticate_drive()
    file_metadata = {'name': file.name}
    media = MediaIoBaseUpload(io.BytesIO(file.getvalue()), mimetype=file.type)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')