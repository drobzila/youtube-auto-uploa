import os
import datetime
import random
import google.auth.transport.requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# إعداد الاعتماديات من المتغيرات البيئية
YOUTUBE_CLIENT_ID = os.environ['YOUTUBE_CLIENT_ID']
YOUTUBE_CLIENT_SECRET = os.environ['YOUTUBE_CLIENT_SECRET']
YOUTUBE_REFRESH_TOKEN = os.environ['YOUTUBE_REFRESH_TOKEN']

DRIVE_CLIENT_ID = os.environ['DRIVE_CLIENT_ID']
DRIVE_CLIENT_SECRET = os.environ['DRIVE_CLIENT_SECRET']
DRIVE_REFRESH_TOKEN = os.environ['DRIVE_REFRESH_TOKEN']

# المسار إلى سجل الفيديوهات المرفوعة
LOG_FILE = "log.txt"

# إعداد YouTube API
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_authenticated_service():
    creds = Credentials(
        None,
        refresh_token=YOUTUBE_REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=YOUTUBE_CLIENT_ID,
        client_secret=YOUTUBE_CLIENT_SECRET,
        scopes=SCOPES,
    )
    creds.refresh(Request())
    return build("youtube", "v3", credentials=creds)

# إعداد Google Drive

def authenticate_drive():
    gauth = GoogleAuth()
    gauth.LoadCredentials()
    gauth.settings["client_config"] = {
        "client_id": DRIVE_CLIENT_ID,
        "client_secret": DRIVE_CLIENT_SECRET,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }
    gauth.credentials = Credentials(
        None,
        refresh_token=DRIVE_REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=DRIVE_CLIENT_ID,
        client_secret=DRIVE_CLIENT_SECRET,
        scopes=['https://www.googleapis.com/auth/drive']
    )
    gauth.Refresh()
    return GoogleDrive(gauth)

def read_log():
    if not os.path.exists(LOG_FILE):
        return set()
    with open(LOG_FILE, "r") as f:
        return set(line.strip() for line in f if line.strip())

def write_to_log(video_id):
    with open(LOG_FILE, "a") as f:
        f.write(video_id + "\n")

def get_unuploaded_videos(drive):
    uploaded = read_log()
    file_list = drive.ListFile({'q': "mimeType contains 'video/' and trashed=false"}).GetList()
    videos = []
    for file in file_list:
        if file['title'] not in uploaded:
            videos.append(file)
    return videos

def get_optimal_publish_times(start_hour=16, count=3):
    now = datetime.datetime.utcnow()
    today = now.date()
    base = datetime.datetime.combine(today, datetime.time(hour=start_hour))
    times = []
    offset_minutes = [0, 60, 120, 180, 240, 300]
    random.shuffle(offset_minutes)

    i = 0
    while len(times) < count:
        candidate = base + datetime.timedelta(minutes=offset_minutes[i % len(offset_minutes)])
        if candidate > now + datetime.timedelta(minutes=15):  # ضمان أن الوقت مستقبلي بما يكفي
            times.append(candidate.isoformat("T") + "Z")
        else:
            base += datetime.timedelta(days=1)
        i += 1
    return times

def upload_video(youtube, file_path, title, publish_time):
    body = {
        "snippet": {
            "title": title,
            "description": "",
            "tags": [],
            "categoryId": "22",
        },
        "status": {
            "privacyStatus": "public",
            "publishAt": publish_time,
            "madeForKids": False
        },
    }

    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=media,
    )
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload progress: {int(status.progress() * 100)}%")

    print(f"Upload complete: {response['id']}")
    write_to_log(title)

def main():
    youtube = get_authenticated_service()
    drive = authenticate_drive()
    videos = get_unuploaded_videos(drive)[:3]
    publish_times = get_optimal_publish_times()

    for file, publish_time in zip(videos, publish_times):
        file_path = file['title']
        print(f"Downloading: {file['title']}")
        file.GetContentFile(file_path)
        upload_video(youtube, file_path, file['title'], publish_time)
        os.remove(file_path)

if __name__ == "__main__":
    main()
