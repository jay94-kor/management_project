from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import streamlit as st
import json
import os

def authenticate_drive():
    gauth = GoogleAuth()
    
    # Streamlit 시크릿에서 클라이언트 설정 정보 가져오기
    service_account_info = json.loads(st.secrets["gcp_service_account"]["service_account_info"])
    
    # 서비스 계정 인증 설정
    settings = {
        "client_config_backend": "service_account",
        "service_account_info": service_account_info
    }
    
    gauth.settings.update(settings)
    gauth.ServiceAuth()
    
    drive = GoogleDrive(gauth)
    return drive

def upload_to_drive(file):
    drive = authenticate_drive()
    
    # 파일 업로드
    gfile = drive.CreateFile({'title': file.name})
    gfile.SetContentFile(file.name)
    gfile.Upload()
    
    return gfile['id']

def get_file_id(file_name):
    drive = authenticate_drive()
    file_list = drive.ListFile({'q': f"title='{file_name}' and trashed=false"}).GetList()
    if file_list:
        return file_list[0]['id']
    else:
        raise FileNotFoundError(f"File named '{file_name}' not found in Google Drive.")

def list_drive_files():
    drive = authenticate_drive()
    file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
    return [{'title': file['title'], 'id': file['id']} for file in file_list if file['mimeType'] == 'application/vnd.google-apps.spreadsheet']