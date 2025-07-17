import os
import json
import google.auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
import io
from googleapiclient.discovery import build

# تحميل بيانات الاعتماد من البيئة
def load_credentials_from_env():
    youtube_service_credentials_json = os.environ.get('YOUTUBE_SERVICE_ACCOUNT_JSON')
    
    if youtube_service_credentials_json is None:
        raise ValueError("مفقود متغير البيئة YOUTUBE_SERVICE_ACCOUNT_JSON.")
    
    # تحميل البيانات من JSON
    credentials_info = json.loads(youtube_service_credentials_json)
    
    return credentials_info

def authenticate_youtube_service_account(credentials_info):
    # التوثيق باستخدام حساب الخدمة
    creds = Credentials.from_service_account_info(
        credentials_info,
        scopes=["https://www.googleapis.com/auth/youtube.upload"]
    )
    youtube_service = build("youtube", "v3", credentials=creds)
    return youtube_service

def authenticate_drive_service(credentials_info):
    # التوثيق باستخدام حساب الخدمة للوصول إلى Google Drive
    creds = Credentials.from_service_account_info(
        credentials_info,
        scopes=["https://www.googleapis.com/auth/drive.readonly"]
    )
    drive_service = build('drive', 'v3', credentials=creds)
    return drive_service

def download_video_from_drive(drive_service, file_id, file_path):
    try:
        # تحميل الفيديو من Google Drive باستخدام file_id
        request = drive_service.files().get_media(fileId=file_id)
        fh = io.FileIO(file_path, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"تحميل {int(status.progress() * 100)}%.")
        print(f"تم تنزيل الفيديو بنجاح إلى {file_path}.")
    except HttpError as error:
        print(f"حدث خطأ أثناء تنزيل الفيديو: {error}")
        
def upload_video_to_youtube(youtube_service, file_path, title, description):
    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": ["auto-uploaded"],
        },
        "status": {
            "privacyStatus": "public",
        },
    }

    media = MediaFileUpload(file_path, mimetype="video/*", resumable=True)

    upload_request = youtube_service.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media
    )

    upload_request.execute()
    print("تم رفع الفيديو إلى YouTube بنجاح!")

def main():
    try:
        youtube_service_credentials_info = load_credentials_from_env()
        youtube_service = authenticate_youtube_service_account(youtube_service_credentials_info)
        drive_service = authenticate_drive_service(youtube_service_credentials_info)

        # اختر الفيديو هنا باستخدام معرف الملف (File ID)
        file_id = "YOUR_VIDEO_FILE_ID"  # قم بتحديد المعرف الصحيح للفيديو
        video_file_path = "/tmp/video.mp4"  # مسار تخزين الفيديو المحلي بعد تحميله
        
        # تنزيل الفيديو من Google Drive
        download_video_from_drive(drive_service, file_id, video_file_path)
        
        # رفع الفيديو إلى YouTube
        upload_video_to_youtube(youtube_service, video_file_path, "Test Video", "Uploaded via service account.")
    
    except Exception as e:
        print(f"حدث خطأ أثناء التوثيق أو رفع الفيديو: {str(e)}")

if __name__ == "__main__":
    main()
