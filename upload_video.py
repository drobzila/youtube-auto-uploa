import os
import io
import google.auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account

# تحميل ملف secrets من السر (GOOGLE_APPLICATION_CREDENTIALS) الموجود في GitHub
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")  # تحميل السر من GitHub Secrets

if not SERVICE_ACCOUNT_FILE:
    raise ValueError("The GOOGLE_APPLICATION_CREDENTIALS secret is not set properly.")

# إعداد الأذونات والخدمة
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# المصادقة باستخدام Service Account
credentials = service_account.Credentials.from_service_account_info(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# بناء الخدمة الخاصة بـ Google Drive API
service = build('drive', 'v3', credentials=credentials)

# دالة لتحميل الملفات من Google Drive
def download_file(file_id, file_name):
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(file_name, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print(f"Download {int(status.progress() * 100)}%.")
    print(f"File {file_name} downloaded successfully.")

# الحصول على جميع الملفات من مجلد معين في Google Drive
folder_id = '1_iPtcfFs3TpusMr9THwTc31SWtLtwccZ'  # استبدل بهذا مع الـ Folder ID الخاص بك
query = f"'{folder_id}' in parents and mimeType='video/mp4'"

# البحث عن الملفات
results = service.files().list(q=query, fields="files(id, name)").execute()
items = results.get('files', [])

if not items:
    print('No files found.')
else:
    # تحميل أول 3 ملفات فقط من القائمة
    for item in items[:3]:
        file_id = item['id']
        file_name = item['name']
        print(f"Downloading file: {file_name}")
        download_file(file_id, file_name)
