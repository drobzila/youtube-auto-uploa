import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import googleapiclient.discovery
from googleapiclient.http import MediaFileUpload

# الأذونات المطلوبة
SCOPES_YOUTUBE = ['https://www.googleapis.com/auth/youtube.upload']
SCOPES_DRIVE = ['https://www.googleapis.com/auth/drive.readonly']

# دالة لتوثيق Drive API
def authenticate_drive():
    creds = Credentials(
        token=None,
        refresh_token=os.getenv('DRIVE_REFRESH_TOKEN'),
        client_id=os.getenv('DRIVE_CLIENT_ID'),
        client_secret=os.getenv('DRIVE_CLIENT_SECRET'),
        token_uri='https://oauth2.googleapis.com/token'
    )
    
    creds.refresh(Request())
    
    return creds

# دالة لتوثيق YouTube API
def authenticate_youtube():
    creds = Credentials(
        token=None,
        refresh_token=os.getenv('YOUTUBE_REFRESH_TOKEN'),
        client_id=os.getenv('YOUTUBE_CLIENT_ID'),
        client_secret=os.getenv('YOUTUBE_CLIENT_SECRET'),
        token_uri='https://oauth2.googleapis.com/token'
    )
    
    creds.refresh(Request())
    
    return creds

# دالة لتحميل الفيديو إلى YouTube
def upload_video(file_path, title, description):
    # توثيق Drive و YouTube
    drive_creds = authenticate_drive()
    youtube_creds = authenticate_youtube()

    # بناء YouTube API
    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=youtube_creds)
    
    media = MediaFileUpload(file_path, resumable=True)
    
    request = youtube.videos().insert(
        part="snippet, status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": ["upload", "test"]
            },
            "status": {
                "privacyStatus": "private"
            }
        },
        media_body=media
    )
    
    response = request.execute()
    print(f"Video uploaded successfully! Video ID: {response['id']}")

if __name__ == "__main__":
    # مثال على كيفية رفع الفيديو
    upload_video('path/to/video.mp4', 'Test Video', 'This is a test video uploaded via script.')
