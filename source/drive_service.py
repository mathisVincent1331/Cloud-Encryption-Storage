import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

import config
from auth import is_user_authorized
from crypto import decrypt_file


# Google Drive Authentication
def authenticate_google_drive():
    config.ensure_directories()
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    creds = None

    if os.path.exists(config.TOKEN_PATH):
        with open("../cred/token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("../cred/credentials.json", SCOPES)
            creds = flow.run_local_server(port=8080)
        with open("../cred/token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return build("drive", "v3", credentials=creds)


# Upload File to Google Drive
def upload_to_drive(file_path, service):
    file_metadata = {
        "name": os.path.basename(file_path),
        "parents": [config.FOLDER_ID]}
    
    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    print(f"Uploaded file {file_path} to Google Drive with ID: {file['id']}")
    return file['id']


# Find File ID by the name
def get_file_id_by_name(file_name, service):
    # Escape single quotes to prevent Drive query syntax errors
    safe_file_name = file_name.replace("'", "\\'")
    query = f"name='{safe_file_name}' and '{config.FOLDER_ID}' in parents and trashed=false"

    response = service.files().list(q=query, spaces='drive', fields='files(id, name)',pageSize=10).execute()
    files = response.get('files', [])

    if not files:
        print(f"No file found with name: {file_name} in folder {config.FOLDER_ID}")
        return None
    
    file_id = files[0]['id']
    print(f"Found file '{file_name}' with ID: {file_id}")
    return file_id


# Download and decrypt the file from Google Drive
def download_and_decrypt_from_drive(file_id, service, aes_key, username):
    if not is_user_authorized(username):
        print("Access Denied: You are not part of the Secure Cloud Storage Group.")
        return
    
    request = service.files().get_media(fileId=file_id)
    downloaded_enc_path = f"downloaded_{file_id}.enc"

    with open(downloaded_enc_path, 'wb') as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Download progress: {int(status.progress() * 100)}%")

    decrypt_file(downloaded_enc_path, aes_key, username)