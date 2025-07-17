import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload  # استيراد MediaFileUpload بشكل صحيح

# الحصول على معلومات التوثيق من البيئة
CLIENT_ID = os.getenv('YOUTUBE_CLIENT_ID')
CLIENT_SECRET = os.getenv('YOUTUBE_CLIENT_SECRET')
REFRESH_TOKEN = os.getenv('YOUTUBE_REFRESH_TOKEN')

# إعدادات API
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

# تحديث بيانات التوثيق باستخدام Refresh Token
credentials = Credentials.from_authorized_user_info(
    info={
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': REFRESH_TOKEN,
    },
    scopes=SCOPES,
)

# بناء عميل YouTube API باستخدام بيانات التوثيق
youtube = build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

# دالة رفع الفيديو
def upload_video(file_path, title, description, category_id=22):
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'categoryId': category_id
        },
        'status': {
            'privacyStatus': 'private'  # يمكن تغييرها إلى "public" أو "unlisted"
        }
    }

    # تحميل الفيديو باستخدام MediaFileUpload
    media = MediaFileUpload(file_path, resumable=True)
    
    # إجراء طلب لرفع الفيديو إلى YouTube
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    # تنفيذ الطلب
    response = request.execute()
    
    # طباعة ID الفيديو الذي تم رفعه
    print(f"Video uploaded successfully! Video ID: {response['id']}")

# تحديد المسار الصحيح للفيديو داخل المجلد "youtube-auto-uploa/videos"
upload_video('youtube-auto-uploa/videos/test_video.mp4', 'Test Video', 'This is a test video uploaded via GitHub Actions.')
