from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import streamlit as st
import json
import os

def authenticate_drive():
    gauth = GoogleAuth()
    
    # Streamlit 시크릿에서 클라이언트 설정 정보 가져오기
    client_config = json.loads(st.secrets["gcp_service_account"]["client_config"])
    client_secrets_file = "client_secrets.json"
    
    # 클라이언트 설정 정보를 파일로 저장
    with open(client_secrets_file, 'w') as f:
        json.dump(client_config, f)
    
    gauth.DEFAULT_SETTINGS['client_config_file'] = client_secrets_file
    gauth.LoadCredentialsFile("credentials/mycreds.txt")
    
    if gauth.credentials is None:
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()
    
    gauth.SaveCredentialsFile("credentials/mycreds.txt")
    
    # 임시 파일 삭제
    os.remove(client_secrets_file)
    
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