from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
import io, os

# كتابة ملف الاعتماد من GitHub Secrets
with open("client_secret.json", "w") as f:
    f.write(os.environ['GOOGLE_CREDS'])

SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/youtube.upload'
]
FOLDER_ID = '1_iPtcfFs3TpusMr9THwTc31SWtLtwccZ'

def download_videos(creds):
    service = build('drive', 'v3', credentials=creds)
    query = f"'{FOLDER_ID}' in parents and mimeType contains 'video/' and trashed=false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get('files', [])
    os.makedirs('downloaded_videos', exist_ok=True)
    for item in items:
        path = os.path.join('downloaded_videos', item['name'])
        if os.path.exists(path):
            continue  # لا تعيد تحميل الملفات
        request = service.files().get_media(fileId=item['id'])
        fh = io.FileIO(path, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        fh.close()
        print(f"✔ تم تحميل: {item['name']}")

def upload_to_youtube(creds):
    youtube = build('youtube', 'v3', credentials=creds)
    folder = 'downloaded_videos'
    for filename in os.listdir(folder):
        filepath = os.path.join(folder, filename)
        print(f"⬆️ رفع: {filename}")
        request_body = {
            'snippet': {
                'title': filename,
                'description': 'تم الرفع تلقائيًا من Google Drive',
                'tags': ['قرآن', 'تلقائي'],
                'categoryId': '22'  # People & Blogs
            },
            'status': {
                'privacyStatus': 'public'
            }
        }
        media = MediaFileUpload(filepath, mimetype='video/*', resumable=True)
        response_upload = youtube.videos().insert(
            part='snippet,status',
            body=request_body,
            media_body=media
        ).execute()
        print(f"✅ تم رفع الفيديو: https://youtu.be/{response_upload['id']}")

def main():
    creds = service_account.Credentials.from_service_account_file("client_secret.json", scopes=SCOPES)
    download_videos(creds)
    upload_to_youtube(creds)

if __name__ == '__main__':
    main()
