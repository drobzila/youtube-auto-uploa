import os
import json
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
import pickle
import time
from datetime import datetime

# تحميل بيانات الاعتماد من البيئة بدلاً من تحميلها من ملف
def load_credentials_from_env():
    # قراءة بيانات الـ Google Drive credentials من secret
    google_drive_credentials_json = os.environ['GOOGLE_DRIVE_CREDENTIALS']
    google_drive_credentials_info = json.loads(google_drive_credentials_json)

    # قراءة بيانات الـ YouTube OAuth من secret
    client_secrets_json = os.environ['CLIENT_SECRETS_JSON']
    client_secrets_info = json.loads(client_secrets_json)

    return google_drive_credentials_info, client_secrets_info

# توثيق الوصول إلى Google Drive باستخدام Service Account
def authenticate_google_drive(credentials_info):
    credentials = ServiceAccountCredentials.from_service_account_info(
        credentials_info,
        scopes=['https://www.googleapis.com/auth/drive']
    )
    drive_service = build('drive', 'v3', credentials=credentials)
    return drive_service

# توثيق الوصول إلى YouTube باستخدام OAuth 2.0
def authenticate_youtube_oauth(client_secrets_info):
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    creds = None
    
    # إذا كان هناك ملف credentials المحفوظ سابقًا
    if os.path.exists('token_youtube.pickle'):
        with open('token_youtube.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # إذا لم يكن هناك توثيق، قم بعمل توثيق جديد
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(client_secrets_info, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # حفظ بيانات التوثيق لتستخدم لاحقًا
        with open('token_youtube.pickle', 'wb') as token:
            pickle.dump(creds, token)

    youtube_service = build('youtube', 'v3', credentials=creds)
    return youtube_service

# الحصول على الملفات من Google Drive
def list_drive_files(drive_service, folder_id):
    results = drive_service.files().list(q=f"'{folder_id}' in parents", spaces='drive').execute()
    files = results.get('files', [])
    
    # تسجيل أسماء الملفات المسترجعة
    print(f"عدد الملفات المسترجعة: {len(files)}")
    for file in files:
        print(f"الملف: {file['name']}")

    return files

# رفع الفيديو إلى YouTube
def upload_video_to_youtube(youtube_service, file_path, title, description):
    request_body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': ['auto-uploaded'],
        },
        'status': {
            'privacyStatus': 'public',  # يمكن تغييره إلى 'private' أو 'unlisted'
        },
    }

    media = MediaFileUpload(file_path, mimetype='video/*', resumable=True)

    upload_request = youtube_service.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media
    )

    upload_request.execute()

# تحميل الفيديو من Google Drive
def download_video(drive_service, file_id):
    request = drive_service.files().get_media(fileId=file_id)
    file_name = f"video_{file_id}.mp4"
    with open(file_name, 'wb') as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
    return file_name

# جدولة رفع الفيديوهات
def schedule_videos(drive_service, youtube_service):
    folder_id = '1_iPtcfFs3TpusMr9THwTc31SWtLtwccZ'  # ID المجلد الخاص بك في Google Drive
    
    # الحصول على الملفات من Google Drive
    files = list_drive_files(drive_service, folder_id)

    # تأكد أن هناك ما يكفي من الملفات
    if len(files) < 3:
        print(f"عدد الملفات في المجلد غير كافٍ، يجب أن يحتوي على 3 ملفات على الأقل. الملفات المتاحة: {len(files)}")
        return

    # وقت التحميل لكل فيديو
    times_to_upload = [
        {"time": datetime.strptime("12:00", "%H:%M"), "index": 0},  # الفيديو الأول في الساعة 12:00
        {"time": datetime.strptime("16:00", "%H:%M"), "index": 1},  # الفيديو الثاني في الساعة 16:00
        {"time": datetime.strptime("20:00", "%H:%M"), "index": 2},  # الفيديو الثالث في الساعة 20:00
    ]
    
    now = datetime.now()

    for upload_time in times_to_upload:
        # تحقق من فهرس الفيديو إذا كان ضمن النطاق
        if upload_time["index"] < len(files):
            video_file = files[upload_time["index"]]
            print(f"تحميل الفيديو: {video_file['name']} من Google Drive")
            
            video_path = download_video(drive_service, video_file['id'])
            
            # حساب الفرق بين الوقت الحالي ووقت التحميل المحدد
            wait_time = (upload_time["time"] - now).total_seconds()

            if wait_time > 0:
                print(f"Waiting {wait_time / 60} minutes for the next upload at {upload_time['time']}")
                time.sleep(wait_time)  # الانتظار حتى الوقت المحدد
            
            # رفع الفيديو إلى YouTube
            print(f"Uploading video {video_file['name']} to YouTube...")
            upload_video_to_youtube(youtube_service, video_path, video_file['name'], 'Video uploaded via script')
        else:
            print(f"الملف المطلوب بالترتيب {upload_time['index']} غير موجود في القائمة.")

# الوظيفة الرئيسية
def main():
    # قراءة الـ credentials من البيئة (GitHub Secrets)
    google_drive_credentials_info, client_secrets_info = load_credentials_from_env()

    try:
        # توثيق الوصول إلى Google Drive باستخدام Service Account
        drive_service = authenticate_google_drive(google_drive_credentials_info)
        
        # توثيق الوصول إلى YouTube باستخدام OAuth 2.0
        youtube_service = authenticate_youtube_oauth(client_secrets_info)
        
        # جدولة رفع الفيديوهات
        schedule_videos(drive_service, youtube_service)
    except Exception as e:
        print(f"حدث خطأ أثناء التوثيق أو رفع الفيديو: {str(e)}")

if __name__ == "__main__":
    main()
