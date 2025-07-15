import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
CLIENT_SECRET = 'client_secret.json'  # سيتم تعبئته من المتغيرات البيئية
TOKEN_PICKLE = 'token_upload.pickle'

def upload_to_youtube():
    # تحميل الإعتمادات
    creds = service_account.Credentials.from_service_account_file(CLIENT_SECRET, scopes=SCOPES)
    youtube = build('youtube', 'v3', credentials=creds)

    folder_path = './downloaded_videos'  # تأكد من أن هذا المجلد يحتوي على الفيديوهات

    # تصفح الملفات في المجلد وتحميلها
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        if os.path.isfile(file_path):
            print(f"⬆️ رفع الفيديو: {filename}")
            request_body = {
                'snippet': {
                    'title': filename,
                    'description': 'تم الرفع تلقائيًا من Google Drive',
                    'tags': ['تلقائي'],
                    'categoryId': '22',  # People & Blogs
                },
                'status': {
                    'privacyStatus': 'public',
                }
            }

            media = MediaFileUpload(file_path, mimetype='video/*', resumable=True)

            response = youtube.videos().insert(
                part='snippet,status',
                body=request_body,
                media_body=media
            ).execute()

            print(f"✅ تم رفع الفيديو: https://youtu.be/{response['id']}")

if __name__ == '__main__':
    upload_to_youtube()
