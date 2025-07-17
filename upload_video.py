import os
import io
import google.auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials

# إعداد تصاريح Google API من ملف الخدمة (service account)
def get_drive_service():
    credentials = ServiceAccountCredentials.from_service_account_info(
        {
            'type': os.getenv('GOOGLE_APPLICATION_CREDENTIALS_TYPE'),
            'project_id': os.getenv('GOOGLE_APPLICATION_CREDENTIALS_PROJECT_ID'),
            'private_key_id': os.getenv('GOOGLE_APPLICATION_CREDENTIALS_PRIVATE_KEY_ID'),
            'private_key': os.getenv('GOOGLE_APPLICATION_CREDENTIALS_PRIVATE_KEY'),
            'client_email': os.getenv('GOOGLE_APPLICATION_CREDENTIALS_CLIENT_EMAIL'),
            'client_id': os.getenv('GOOGLE_APPLICATION_CREDENTIALS_CLIENT_ID'),
            'auth_uri': os.getenv('GOOGLE_APPLICATION_CREDENTIALS_AUTH_URI'),
            'token_uri': os.getenv('GOOGLE_APPLICATION_CREDENTIALS_TOKEN_URI'),
            'auth_provider_x509_cert_url': os.getenv('GOOGLE_APPLICATION_CREDENTIALS_AUTH_PROVIDER_X509_CERT_URL'),
            'client_x509_cert_url': os.getenv('GOOGLE_APPLICATION_CREDENTIALS_CLIENT_X509_CERT_URL')
        },
        scopes=["https://www.googleapis.com/auth/drive.readonly", "https://www.googleapis.com/auth/youtube.upload"]
    )
    drive_service = build('drive', 'v3', credentials=credentials)
    return drive_service

# تحميل الفيديو من Google Drive
def download_video_from_drive(file_id, file_name, drive_service):
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.FileIO(file_name, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print(f"Download {int(status.progress() * 100)}%.")
    return file_name

# إعداد التصريحات من Google API
def get_youtube_service():
    credentials = Credentials.from_authorized_user_info(
        {
            'client_id': os.getenv('YOUTUBE_CLIENT_ID'),
            'client_secret': os.getenv('YOUTUBE_CLIENT_SECRET'),
            'refresh_token': os.getenv('YOUTUBE_REFRESH_TOKEN'),
        },
        scopes=["https://www.googleapis.com/auth/youtube.upload"]
    )
    youtube_service = build('youtube', 'v3', credentials=credentials)
    return youtube_service

# رفع الفيديو إلى YouTube
def upload_video_to_youtube(file_path, title, description, youtube_service):
    media = MediaFileUpload(file_path, mimetype="video/*", resumable=True)

    request = youtube_service.videos().insert(
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

    response = request.execute()
    print(f"Video uploaded successfully! Video ID: {response['id']}")

# تنفيذ العملية
def main():
    # معرف المجلد في Google Drive
    folder_id = 'your_drive_folder_id'  # ضع هنا معرف المجلد في Google Drive الذي يحتوي على الفيديوهات

    # إعداد Google Drive API
    drive_service = get_drive_service()

    # استرداد الملفات من المجلد
    results = drive_service.files().list(q=f"'{folder_id}' in parents", fields="files(id, name)").execute()
    files = results.get('files', [])

    if not files:
        print("No files found in this folder.")
        return

    # اختر الفيديو الأول من المجلد
    video = files[0]
    video_id = video['id']
    video_name = video['name']

    print(f"Found video: {video_name}, downloading...")

    # تنزيل الفيديو من Google Drive
    downloaded_video_path = download_video_from_drive(video_id, video_name, drive_service)

    # إعداد YouTube API
    youtube_service = get_youtube_service()

    # رفع الفيديو إلى YouTube
    upload_video_to_youtube(downloaded_video_path, 'Test Video from Drive', 'This video was uploaded from Google Drive using script.', youtube_service)

if __name__ == '__main__':
    main()
