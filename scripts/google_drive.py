from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import streamlit as st

def authenticate_drive():
    gauth = GoogleAuth()
    gauth.DEFAULT_SETTINGS['client_config_file'] = "credentials/client_secrets.json"
    gauth.LoadCredentialsFile("credentials/mycreds.txt")
    
    if gauth.credentials is None:
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()
    
    gauth.SaveCredentialsFile("credentials/mycreds.txt")
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