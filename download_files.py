import os
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# تحميل الأسرار من البيئة
CLIENT_ID = os.getenv('DRIVE_CLIENT_ID')
CLIENT_SECRET = os.getenv('DRIVE_CLIENT_SECRET')
REFRESH_TOKEN = os.getenv('DRIVE_REFRESH_TOKEN')

# تعريف بعض المتغيرات الأخرى
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']  # تغيير الأذونات حسب الحاجة
FOLDER_ID = '1_iPtcfFs3TpusMr9THwTc31SWtLtwccZ'  # ID المجلد الذي يحتوي على الفيديوهات

# المصادقة مع Google API
def authenticate_drive():
    credentials = Credentials(
        None,
        refresh_token=REFRESH_TOKEN,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        token_uri="https://oauth2.googleapis.com/token"
    )

    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())

    return credentials

# تحميل الملفات من المجلد المحدد
def download_files():
    creds = authenticate_drive()
    try:
        service = build('drive', 'v3', credentials=creds)
        
        # استرجاع الملفات في المجلد
        results = service.files().list(
            q=f"'{FOLDER_ID}' in parents", spaces='drive', fields='files(id, name)').execute()
        items = results.get('files', [])

        if not items:
            print('No files found.')
        else:
            for item in items:
                print(f'Downloading file: {item["name"]}')
                request = service.files().get_media(fileId=item['id'])
                file_path = f'downloaded_videos/{item["name"]}'
                with open(file_path, 'wb') as f:
                    downloader = googleapiclient.http.MediaIoBaseDownload(f, request)
                    done = False
                    while done is False:
                        status, done = downloader.next_chunk()
                        print(f"Download {int(status.progress() * 100)}%.")
        print("All files downloaded successfully!")
    
    except HttpError as error:
        print(f"An error occurred: {error}"
