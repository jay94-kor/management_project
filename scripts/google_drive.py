from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import streamlit as st

def upload_to_drive(file):
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
    
    # 파일 업로드
    gfile = drive.CreateFile({'title': file.name})
    gfile.SetContentFile(file.name)
    gfile.Upload()
    
    return gfile['id']