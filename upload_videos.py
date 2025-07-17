import os
import json
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials

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

def main():
    try:
        youtube_service_credentials_info = load_credentials_from_env()
        youtube_service = authenticate_youtube_service_account(youtube_service_credentials_info)

        # اختر الفيديو هنا أو قم بتحميله من Google Drive
        video_file_path = "your_video_path.mp4"  # قم بتحديد المسار الصحيح للفيديو
        upload_video_to_youtube(youtube_service, video_file_path, "Test Video", "Uploaded via service account.")
    
    except Exception as e:
        print(f"حدث خطأ أثناء التوثيق أو رفع الفيديو: {str(e)}")

if __name__ == "__main__":
    main()
