from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import streamlit as st

def upload_to_drive(file):
    gauth = GoogleAuth()
    gauth.DEFAULT_SETTINGS['client_config_file'] = "client_secrets.json"
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)
    
    # 파일 업로드
    gfile = drive.CreateFile({'title': file.name})
    gfile.SetContentFile(file.name)
    gfile.Upload()
    
    return gfile['id']