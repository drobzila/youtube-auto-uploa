import os
import io
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError
from tempfile import NamedTemporaryFile

# إعدادات الوصول إلى Google Drive API
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
DOWNLOAD_FOLDER = 'downloaded_videos'  # هذا هو المجلد الذي سيتم تحميل الفيديوهات إليه

# استرجاع الأسرار من البيئة
def get_drive_credentials():
    client_id = os.getenv('DRIVE_CLIENT_ID')
    client_secret = os.getenv('DRIVE_CLIENT_SECRET')
    refresh_token = os.getenv('DRIVE_REFRESH_TOKEN')

    if not all([client_id, client_secret, refresh_token]):
        raise ValueError("Missing one or more Drive credentials in environment variables.")
    
    # استخدم هذه القيم لإنشاء بيانات OAuth
    credentials = Credentials(
        None,
        refresh_token=refresh_token,
        client_id=client_id,
        client_secret=client_secret,
        token_uri="https://oauth2.googleapis.com/token"
    )
    
    # تحقق من صحة البيانات
    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())

    return credentials

# تهيئة عملية OAuth2
def authenticate_drive():
    credentials = get_drive_credentials()
    return credentials

def download_file(service, file_id, destination):
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(destination, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print(f'Downloading {destination} {int(status.progress() * 100)}%.')
    print(f'File {destination} downloaded successfully.')

def get_drive_files(credentials):
    try:
        service = build('drive', 'v3', credentials=credentials)
        results = service.files().list(q="'1_iPtcfFs3TpusMr9THwTc31SWtLtwccZ' in parents and mimeType = 'video/mp4'",
                                       fields="files(id, name)").execute()
        items = results.get('files', [])
        return items
    except HttpError as error:
        print(f"An error occurred: {error}")
        return []

def main():
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)

    credentials = authenticate_drive()

    files = get_drive_files(credentials)
    
    if not files:
        print('No files found.')
    else:
        for file in files:
            file_id = file['id']
            file_name = file['name']
            destination = os.path.join(DOWNLOAD_FOLDER, file_name)
            download_file(service=build('drive', 'v3', credentials=credentials), file_id=file_id, destination=destination)

if __name__ == '__main__':
    main()
