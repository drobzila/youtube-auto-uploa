import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
import io
import pickle
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# تعريف أذونات API
SCOPES = ['https://www.googleapis.com/auth/drive.readonly', 'https://www.googleapis.com/auth/youtube.upload']

# مسار المجلد في Google Drive
DRIVE_FOLDER_ID = "1_iPtcfFs3TpusMr9THwTc31SWtLtwccZ"  # تغيير هذا إلى ID المجلد الخاص بك

# مصادقة حساب Google Drive
def authenticate_drive():
    creds = None
    if os.path.exists('token_drive.pickle'):
        with open('token_drive.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # استخدام بيانات المصادقة من أسرار البيئة
            drive_client_id = os.getenv('DRIVE_CLIENT_ID')
            drive_client_secret = os.getenv('DRIVE_CLIENT_SECRET')
            flow = InstalledAppFlow.from_client_secrets_file(
                'drive_client_secrets.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token_drive.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    drive_service = build('drive', 'v3', credentials=creds)
    return drive_service

# تحميل فيديو من Google Drive
def download_file_from_drive(drive_service, file_id, destination_path):
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.FileIO(destination_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print(f"Download {int(status.progress() * 100)}%.")
    
    print("Download complete.")
    return destination_path

# رفع الفيديو إلى YouTube
def upload_video(file_path, title, description):
    # استخدام بيانات المصادقة المخزنة كأسرار في البيئة
    youtube_client_id = os.getenv('YOUTUBE_CLIENT_ID')
    youtube_client_secret = os.getenv('YOUTUBE_CLIENT_SECRET')
    youtube_refresh_token = os.getenv('YOUTUBE_REFRESH_TOKEN')

    credentials = Credentials.from_authorized_user_info(
        client_id=youtube_client_id,
        client_secret=youtube_client_secret,
        refresh_token=youtube_refresh_token
    )

    youtube_service = build('youtube', 'v3', credentials=credentials)

    # إعداد الفيديو الذي سيتم رفعه
    media = MediaFileUpload(file_path, resumable=True)
    request = youtube_service.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description
            },
            "status": {
                "privacyStatus": "private"  # يمكن تعديلها إلى public أو unlisted حسب الحاجة
            }
        },
        media_body=media
    )

    # رفع الفيديو
    response = request.execute()
    print(f"Video uploaded successfully! Video ID: {response['id']}")

# الحصول على قائمة الملفات من Google Drive
def get_files_from_drive(drive_service):
    results = drive_service.files().list(
        q=f"'{DRIVE_FOLDER_ID}' in parents",
        fields="files(id, name)"
    ).execute()
    return results.get('files', [])

# تنفيذ الكود
if __name__ == "__main__":
    drive_service = authenticate_drive()
    files = get_files_from_drive(drive_service)

    # تحميل 3 فيديوهات عشوائية
    for i in range(3):
        file_id = files[i]['id']
        file_name = files[i]['name']
        print(f"Downloading {file_name}...")
        
        # تنزيل الفيديو من Drive
        download_path = f'./downloads/{file_name}'
        download_file_from_drive(drive_service, file_id, download_path)

        # رفع الفيديو إلى YouTube
        upload_video(download_path, file_name, f"This is a video uploaded from Drive: {file_name}")
