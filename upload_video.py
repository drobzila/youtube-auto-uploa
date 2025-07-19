import os
import io
import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from google.auth.transport.requests import Request

LOG_FILE = "log.txt"

# إعداد Google Drive API
def get_drive_service():
    credentials = ServiceAccountCredentials.from_service_account_info(
        {
            ""type": "service_account",
            "project_id": "able-rarity-466017-d7",
            "private_key_id": "079b667528615f3d89d4e5ee88763e8bf4d0075b",
            "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCufxjiyqBw8YSB\nfCVVulCVMYEuJ3f3Wqv+lwJszEi/qp4KbYS7iLNtiInoZbrGPMrGb5eN5DXjvjkB\ndu1Rw2iWlcuXyCRUWy3TiRG1Zcjmwx/NY/9fXmzWSi7bmN0w7vTKigmhDxsYJGSj\n3PBnrTE932DQWltAQ20XVnJPl/3ZZc6HJOanNAus6AjVVbCOQfQFxb71yFOkygE/\np2drYdR5tZBYHiwP+1Gr2WtczdhDXFgKCrQsiJcrjdzz244F87/OH0hTRNUhLaG6\neX1Eb7Djo+ACGutooSF0Y1PQa2hB7F+r9dPFL6Ge7BGFhhQPbebbO0bTgBUKIwoP\nFSQ6OLpjAgMBAAECggEARZ8/aimnpziuAk3qxZAvm79jR+uGgaJjUpKk7Iz7j8G/\nCfEVjw+la5QZVijUw0i5LUCUCxCdcc9RhmSRnthlMAP3dglseV3h5G9hqetBI9WB\nqFz4JPCTY1K47HRK+L223OMDoYfZ6yGGKB08rFkddw7b3XXXx8W/Tpr2xAwkRCsh\nYdLcRJgQrOD7gOtIkbnvGDUBE0IMNGn23Smwh6bpDkvdEDS7znmuYFaMNnvGtdXJ\nImZPKN+JpsdiOXiypownCkludgXIH0eVgLvGMxYPqKs4xqtV0sp8GPnjqlsv+tI+\n+n0tVei+U4RMSJQEyA4HLOgBKrefzhGzuJWtm60tlQKBgQDs1rtTW9A9xlz6n/sV\ndEk/lflxBqCRf1gtb5aDjGfGDuCQcWuVThA0dsLnKzKCWfuD0gWp/g+PWk2EPdaG\nCLN3T0zuk6r7dZPz3AElL/VpoZn252GKRoW37QOD7ZQvAy8ae8QXuoaQw1rEruQ0\ni86jIpNYejsrXnJKLtDVM5embQKBgQC8nSrVcBIT4bhOn84lPJg6jAC1dB7FdKuk\nEwaZRBxKbe+y7z3YWFr1joXDKMzyGp5HFzuUoh42Dvf6IQNU1xh4Z44yxOFkGUiA\nK4Q8JlohNLmkFZQKHwtrxCl3Do96O4plsweLlEGrOkMuUEwqdSswceo0kSdmXzWD\nFy5msfmiDwKBgFN8hmAmF0wPZqs6RcoUSdXOSjXbfjKLz0uE8GvCzLn2eJayRJhH\nAlNcIexXP+DPU2fuWuzHkDiaPoUFP1/UJV9DZv0atMUbd2IZBZZUR5BK1PlCKxIR\nNgXV2M1irD++QZZ2VnN+3vycwJxggjU7q0W6ZHJl9AGfs24O/rKJE0YpAoGATi7f\n+IVyGOex3HWFoA3UFEDAcnbl4neQRnzUeWewSnHzsDpXanyFh9BCRjl9asX54gIR\nYnUpDMN7qyVQGjTnIdHbMdRGkZWhZe+j6sMDDUyrvwZqzR89Pribb4yLkOFpZuql\nMAiOiAmom2QRjm/vLS+rI4sfx+GjbumHBG61yaUCgYEAyqp6KaH9EMU7wWVI08Xn\nIATOb2GkD/QHO3CCQdfMEulE8vorc8scuUkpPIJ/FHnTEn2aqcZIAQ7TwxUn9SPi\nf6lFEwYlddeLRg4KgtEDdXVywmTdt+/J/aEdWfEpxujmg7Ad9rYOD1YyvCY7SYgL\n+x05lczFEa5jD10b1h0K5LM=\n-----END PRIVATE KEY-----\n",
            "client_email": "googeldrive-uploader-service-a@able-rarity-466017-d7.iam.gserviceaccount.com",
            "client_id": "109947952583981958040",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/googeldrive-uploader-service-a%40able-rarity-466017-d7.iam.gserviceaccount.com",
            "universe_domain": "googleapis.com"
        },
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    return build('drive', 'v3', credentials=credentials)

# إعداد YouTube API
def get_youtube_service():
    creds = Credentials(
        None,
        refresh_token=os.getenv('YOUTUBE_REFRESH_TOKEN'),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv('YOUTUBE_CLIENT_ID'),
        client_secret=os.getenv('YOUTUBE_CLIENT_SECRET'),
        scopes=["https://www.googleapis.com/auth/youtube.upload"]
    )
    creds.refresh(Request())
    return build('youtube', 'v3', credentials=creds)

# التحقق من الفيديوهات التي تم رفعها سابقًا
def get_uploaded_videos():
    if not os.path.exists(LOG_FILE):
        return set()
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return set(line.strip().split(" - ")[0] for line in f.readlines())

# تحميل فيديو من Google Drive
def download_video_from_drive(file_id, file_name, drive_service):
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.FileIO(file_name, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    return file_name

# رفع فيديو إلى YouTube مع جدولة النشر
def upload_video_to_youtube(file_path, title, youtube_service, publish_datetime):
    media = MediaFileUpload(file_path, mimetype="video/*", resumable=True)

    request = youtube_service.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": "",  # لا يوجد وصف
            },
            "status": {
                "privacyStatus": "private",  # يتم جدولته للنشر لاحقًا
                "selfDeclaredMadeForKids": False,
                "publishAt": publish_datetime.isoformat() + "Z"
            }
        },
        media_body=media
    )

    response = request.execute()
    print(f"✅ تم جدولة: {title} في {publish_datetime.isoformat()} UTC - Video ID: {response['id']}")
    with open(LOG_FILE, "a", encoding="utf-8") as log_file:
        log_file.write(f"{title} - Scheduled at: {publish_datetime} UTC - Video ID: {response['id']}\n")

# البرنامج الرئيسي
def main():
    drive_service = get_drive_service()
    youtube_service = get_youtube_service()

    uploaded_titles = get_uploaded_videos()

    folder_id = '1_iPtcfFs3TpusMr9THwTc31SWtLtwccZ'
    results = drive_service.files().list(q=f"'{folder_id}' in parents", fields="files(id, name)").execute()
    files = results.get('files', [])

    # تصفية الفيديوهات غير المرفوعة فقط
    files_to_upload = [f for f in files if f['name'] not in uploaded_titles][:3]

    if len(files_to_upload) < 3:
        print("❗ يجب توفر 3 فيديوهات غير مرفوعة على الأقل.")
        return

    # تحديد أوقات النشر حسب توقيت الجزائر UTC+1
    now = datetime.datetime.now(datetime.timezone.utc)
    base_date = now.date()

    schedule_times = [
        datetime.datetime.combine(base_date, datetime.time(12, 0), tzinfo=datetime.timezone(datetime.timedelta(hours=1))),
        datetime.datetime.combine(base_date, datetime.time(16, 0), tzinfo=datetime.timezone(datetime.timedelta(hours=1))),
        datetime.datetime.combine(base_date, datetime.time(21, 0), tzinfo=datetime.timezone(datetime.timedelta(hours=1))),
    ]

    # تحويل التواريخ إلى UTC
    schedule_times_utc = [dt.astimezone(datetime.timezone.utc) for dt in schedule_times]

    for i in range(3):
        file = files_to_upload[i]
        file_path = download_video_from_drive(file['id'], file['name'], drive_service)
        upload_video_to_youtube(file_path, file['name'], youtube_service, schedule_times_utc[i])
        os.remove(file_path)  # حذف الملف المحلي بعد الرفع

if __name__ == "__main__":
    main()
