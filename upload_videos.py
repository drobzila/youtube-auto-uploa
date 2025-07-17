import os
import json
import time
import pickle
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from google_auth_oauthlib.flow import InstalledAppFlow

# طباعة المسارات التي تم قراءتها من البيئة
print("GOOGLE_DRIVE_CREDENTIALS =", os.environ.get("GOOGLE_DRIVE_CREDENTIALS"))
print("YOUTUBE_CLIENT_SECRETS =", os.environ.get("YOUTUBE_CLIENT_SECRETS"))

# تحميل بيانات الاعتماد من ملفات JSON الموجودة في المسارات المحددة في المتغيرات البيئية
def load_credentials_from_env():
    google_drive_credentials_path = os.environ.get('GOOGLE_DRIVE_CREDENTIALS')
    youtube_client_secrets_path = os.environ.get('YOUTUBE_CLIENT_SECRETS')

    print(f"Google Drive Credentials JSON: {google_drive_credentials_path}")
    print(f"YouTube Client Secrets JSON: {youtube_client_secrets_path}")

    if google_drive_credentials_path is None or youtube_client_secrets_path is None:
        raise ValueError("One or more of the required environment variables are missing.")

    with open(google_drive_credentials_path, 'r', encoding='utf-8') as f:
        google_drive_credentials_info = json.load(f)

    with open(youtube_client_secrets_path, 'r', encoding='utf-8') as f:
        client_secrets_info = json.load(f)

    return google_drive_credentials_info, client_secrets_info

def authenticate_google_drive(credentials_info):
    credentials = ServiceAccountCredentials.from_service_account_info(
        credentials_info,
        scopes=['https://www.googleapis.com/auth/drive']
    )
    drive_service = build('drive', 'v3', credentials=credentials)
    return drive_service

def authenticate_youtube_oauth(credentials_info):
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    creds = None

    # تحميل التوكن من ملف pickle إذا كان موجودًا
    if os.path.exists('token_youtube.pickle'):
        with open('token_youtube.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(credentials_info, SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token_youtube.pickle', 'wb') as token:
            pickle.dump(creds, token)

    youtube_service = build('youtube', 'v3', credentials=creds)
    return youtube_service

def list_drive_files(drive_service, folder_id):
    results = drive_service.files().list(q=f"'{folder_id}' in parents", spaces='drive').execute()
    files = results.get('files', [])

    print(f"عدد الملفات المسترجعة: {len(files)}")
    for file in files:
        print(f"الملف: {file['name']}")

    return files

def upload_video_to_youtube(youtube_service, file_path, title, description):
    request_body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': ['auto-uploaded'],
        },
        'status': {
            'privacyStatus': 'public',
        },
    }

    media = MediaFileUpload(file_path, mimetype='video/*', resumable=True)

    upload_request = youtube_service.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media
    )

    upload_request.execute()

def download_video(drive_service, file_id):
    request = drive_service.files().get_media(fileId=file_id)
    file_name = f"video_{file_id}.mp4"
    with open(file_name, 'wb') as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
    return file_name

def schedule_videos(drive_service, youtube_service):
    folder_id = '1_iPtcfFs3TpusMr9THwTc31SWtLtwccZ'
    files = list_drive_files(drive_service, folder_id)

    if len(files) < 3:
        print(f"عدد الملفات في المجلد غير كافٍ، يجب أن يحتوي على 3 ملفات على الأقل. الملفات المتاحة: {len(files)}")
        return

    times_to_upload = [
        {"time": datetime.strptime("12:00", "%H:%M"), "index": 0},
        {"time": datetime.strptime("16:00", "%H:%M"), "index": 1},
        {"time": datetime.strptime("20:00", "%H:%M"), "index": 2},
    ]

    now = datetime.now()

    for upload_time in times_to_upload:
        if upload_time["index"] < len(files):
            video_file = files[upload_time["index"]]
            print(f"تحميل الفيديو: {video_file['name']} من Google Drive")
            
            video_path = download_video(drive_service, video_file['id'])

            wait_time = (upload_time["time"] - now).total_seconds()
            if wait_time > 0:
                print(f"الانتظار {wait_time / 60} دقيقة حتى وقت الرفع المحدد: {upload_time['time']}")
                time.sleep(wait_time)

            print(f"رفع الفيديو {video_file['name']} إلى YouTube...")
            upload_video_to_youtube(youtube_service, video_path, video_file['name'], 'Video uploaded via script')
        else:
            print(f"الملف المطلوب بالترتيب {upload_time['index']} غير موجود في القائمة.")

def main():
    try:
        google_drive_credentials_info, client_secrets_info = load_credentials_from_env()
        drive_service = authenticate_google_drive(google_drive_credentials_info)
        youtube_service = authenticate_youtube_oauth(client_secrets_info)
        schedule_videos(drive_service, youtube_service)
    except Exception as e:
        print(f"حدث خطأ أثناء التوثيق أو رفع الفيديو: {str(e)}")

if __name__ == "__main__":
    main()
