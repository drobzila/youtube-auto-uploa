import os
import io
import time
import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from google.auth.transport.requests import Request

# إعداد Google Drive API
def get_drive_service():
    credentials = ServiceAccountCredentials.from_service_account_info(
        {
            "type": "service_account",
            "project_id": "able-rarity-466017-d7",
            "private_key_id": "079b667528615f3d89d4e5ee88763e8bf4d0075b",
            "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
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

# تحميل فيديو من Google Drive
def download_video_from_drive(file_id, file_name, drive_service):
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.FileIO(file_name, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    return file_name

# رفع فيديو إلى YouTube مع جدولة النشر
def upload_video_to_youtube(file_path, title, youtube_service, publish_datetime):
    media = MediaFileUpload(file_path, mimetype="video/*", resumable=True)

    request = youtube_service.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "publishAt": publish_datetime.isoformat() + "Z"  # صيغة UTC ISO
            },
            "status": {
                "privacyStatus": "private",  # سيُنشر تلقائيًا في وقت publishAt
                "selfDeclaredMadeForKids": False,
                "publishAt": publish_datetime.isoformat() + "Z"
            }
        },
        media_body=media
    )

    response = request.execute()
    print(f"✅ Scheduled {title} for {publish_datetime} UTC - Video ID: {response['id']}")
    with open("log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(f"{title} - Scheduled at: {publish_datetime} UTC - Video ID: {response['id']} - Logged at: {datetime.datetime.utcnow().isoformat()}Z\n")

# البرنامج الرئيسي
def main():
    drive_service = get_drive_service()
    youtube_service = get_youtube_service()

    folder_id = '1_iPtcfFs3TpusMr9THwTc31SWtLtwccZ'
    results = drive_service.files().list(q=f"'{folder_id}' in parents", fields="files(id, name)").execute()
    files = results.get('files', [])

    if len(files) < 3:
        print("❗ يلزم وجود على الأقل 3 فديوهات في المجلد.")
        return

    # ضبط التواريخ بالنشر المجدول (بتوقيت الجزائر UTC+1)
    now = datetime.datetime.now(datetime.timezone.utc)
    dates = [
        datetime.datetime.combine(now.date(), datetime.time(12, 0), tzinfo=datetime.timezone(datetime.timedelta(hours=1))),
        datetime.datetime.combine(now.date(), datetime.time(16, 0), tzinfo=datetime.timezone(datetime.timedelta(hours=1))),
        datetime.datetime.combine(now.date(), datetime.time(21, 0), tzinfo=datetime.timezone(datetime.timedelta(hours=1)))
    ]

    # تحويل التواريخ إلى UTC (مطلوب من YouTube API)
    dates_utc = [d.astimezone(datetime.timezone.utc) for d in dates]

    # رفع وجدولة الفيديوهات
    for i in range(3):
        video = files[i]
        path = download_video_from_drive(video['id'], video['name'], drive_service)
        upload_video_to_youtube(path, video['name'], youtube_service, dates_utc[i])

if __name__ == "__main__":
    main()
