from google.oauth2 import service_account
from googleapiclient.discovery import build
import streamlit as st
from googleapiclient.http import MediaIoBaseUpload
import io

SCOPES = ['https://www.googleapis.com/auth/drive']

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

def upload_to_drive(file):
    service = authenticate_drive()
    file_metadata = {'name': file.name}
    media = MediaIoBaseUpload(io.BytesIO(file.getvalue()), mimetype=file.type)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')