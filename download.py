from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io, os

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
FOLDER_ID = '1_iPtcfFs3TpusMr9THwTc31SWtLtwccZ'

def download_videos():
    creds = service_account.Credentials.from_service_account_file("client_secret_drive.json", scopes=SCOPES)
    service = build('drive', 'v3', credentials=creds)

    query = f"'{FOLDER_ID}' in parents and mimeType contains 'video/' and trashed=false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get('files', [])
    os.makedirs('downloaded_videos', exist_ok=True)

    for item in items:
        path = os.path.join('downloaded_videos', item['name'])
        if os.path.exists(path):
            print(f"✔ الفيديو موجود مسبقًا: {item['name']}")
            continue
        request = service.files().get_media(fileId=item['id'])
        fh = io.FileIO(path, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        fh.close()
        print(f"✔ تم تحميل الفيديو: {item['name']}")

if __name__ == '__main__':
    download_videos()
