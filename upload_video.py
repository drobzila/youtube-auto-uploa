import os
import io
import time
import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials

# إعداد Google Drive API
def get_drive_service():
    credentials = Credentials.from_service_account_info(
        {
            "type": "service_account",
            "project_id": "able-rarity-466017-d7",
            "private_key_id": "079b667528615f3d89d4e5ee88763e8bf4d0075b",
            "private_key": "-----BEGIN PRIVATE KEY-----\n...YOUR_KEY...\n-----END PRIVATE KEY-----\n",
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
    credentials = Credentials.from_authorized_user_info(
        {
            'client_id': os.getenv('YOUTUBE_CLIENT_ID'),
            'client_secret': os.getenv('YOUTUBE_CLIENT_SECRET'),
            'refresh_token': os.getenv('YOUTUBE_REFRESH_TOKEN'),
        },
        scopes=["https://www.googleapis.com/auth/youtube.upload"]
    )
    return build('youtube', 'v3', credentials=credentials)

# تحميل فيديو
def download_video_from_drive(file_id, file_name, drive_service):
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.FileIO(file_name, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    return file_name

# رفع فيديو
def upload_video_to_youtube(file_path, title, youtube_service):
    media = MediaFileUpload(file_path, mimetype="video/*", resumable=True)
    request = youtube_service.videos().insert(
        part="snippet,status",
        body={
            "snippet": {"title": title},
            "status": {"privacyStatus": "public", "madeForKids": False}
        },
        media_body=media
    )
    response = request.execute()
    print(f"✅ Uploaded {title} - Video ID: {response['id']}")
    with open("log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(f"{title} - Video ID: {response['id']} - {datetime.datetime.now()}\n")

# الانتظار حتى وقت معين (بالساعة والدقيقة) بتوقيت الجزائر
def wait_until(hour, minute):
    target = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=1)))\
        .replace(hour=hour, minute=minute, second=0, microsecond=0)
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=1)))
    delay = (target - now).total_seconds()
    if delay > 0:
        print(f"🕒 Waiting until {hour}:{minute:02d}...")
        time.sleep(delay)

def main():
    # إعداد الخدمات
    drive_service = get_drive_service()
    youtube_service = get_youtube_service()

    # جلب الفيديوهات من Google Drive
    folder_id = '1_iPtcfFs3TpusMr9THwTc31SWtLtwccZ'
    results = drive_service.files().list(q=f"'{folder_id}' in parents", fields="files(id, name)").execute()
    files = results.get('files', [])

    if len(files) < 2:
        print("❗ يلزم وجود على الأقل فديوهين في المجلد.")
        return

    # رفع الفيديو الأول عند 15:35
    wait_until(15, 35)
    video1 = files[0]
    path1 = download_video_from_drive(video1['id'], video1['name'], drive_service)
    upload_video_to_youtube(path1, video1['name'], youtube_service)

    # رفع الفيديو الثاني عند 15:40
    wait_until(15, 40)
    video2 = files[1]
    path2 = download_video_from_drive(video2['id'], video2['name'], drive_service)
    upload_video_to_youtube(path2, video2['name'], youtube_service)

if __name__ == "__main__":
    main()
