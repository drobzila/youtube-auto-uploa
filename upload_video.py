import os
import google.auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

# إعداد المسار للفيديو باستخدام os
def upload_video(file_path, title, description):
    # التأكد من أن ملف الفيديو موجود
    if not os.path.exists(file_path):
        print(f"Error: The video file at {file_path} does not exist.")
        return

    # إعداد التصريحات باستخدام refresh token
    credentials = Credentials.from_authorized_user_info(
        {
            'client_id': os.getenv('YOUTUBE_CLIENT_ID'),
            'client_secret': os.getenv('YOUTUBE_CLIENT_SECRET'),
            'refresh_token': os.getenv('YOUTUBE_REFRESH_TOKEN'),
        },
        scopes=["https://www.googleapis.com/auth/youtube.upload"]
    )

    # بناء خدمة YouTube API
    youtube = build('youtube', 'v3', credentials=credentials)

    # إعداد ملف الفيديو
    media = MediaFileUpload(file_path, mimetype="video/*", resumable=True)

    # تحميل الفيديو إلى YouTube
    request = youtube.videos().insert(
        part="snippet,status",
        body=dict(
            snippet=dict(
                title=title,
                description=description,
            ),
            status=dict(
                privacyStatus="public",  # يمكنك تغييرها إلى "private" أو "unlisted" حسب رغبتك
            ),
        ),
        media_body=media
    )

    # إجراء تحميل الفيديو
    response = request.execute()

    print(f"Video uploaded successfully! Video ID: {response['id']}")


# المسار الكامل إلى الفيديو باستخدام os
video_path = os.path.join(os.getcwd(), 'videos', 'test_video.mp4')

# قم بتشغيل رفع الفيديو
upload_video(video_path, 'Test Video', 'This is a test video uploaded via GitHub Actions.')
