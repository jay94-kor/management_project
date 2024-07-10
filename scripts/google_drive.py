from google.oauth2 import service_account
from googleapiclient.discovery import build
import streamlit as st

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def authenticate_drive():
    creds = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
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