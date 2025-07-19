import os
import json
import time
import random
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from datetime import datetime, timedelta

# تحميل الأسرار من متغيرات البيئة (GitHub Secrets)
CLIENT_ID = os.environ["YOUTUBE_CLIENT_ID"]
CLIENT_SECRET = os.environ["YOUTUBE_CLIENT_SECRET"]
REFRESH_TOKEN = os.environ["YOUTUBE_REFRESH_TOKEN"]

# إعداد الاعتماديات
def get_authenticated_service():
    creds_data = {
        "token": "",
        "refresh_token": REFRESH_TOKEN,
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scopes": ["https://www.googleapis.com/auth/youtube.upload"]
    }

    creds = Credentials.from_authorized_user_info(info=creds_data)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build("youtube", "v3", credentials=creds)

# تحميل فيديو إلى يوتيوب
def upload_video(youtube, file_path, title, description, publish_time):
    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": ["Quran", "Islam", "Recitation"],
            "categoryId": "27"
        },
        "status": {
            "privacyStatus": "public",
            "publishAt": publish_time.isoformat("T") + "Z",
            "selfDeclaredMadeForKids": False,
        }
    }

    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)

    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload progress: {int(status.progress() * 100)}%")
    print(f"✅ Uploaded: {title}")

    return response["id"]

# قراءة سجل الفيديوهات
def read_uploaded_log():
    if not os.path.exists("log.txt"):
        return set()
    with open("log.txt", "r") as f:
        return set(line.strip() for line in f)

def append_to_log(title):
    with open("log.txt", "a") as f:
        f.write(f"{title}\n")

# توليد أوقات مثالية للنشر
def generate_best_times(n):
    base = datetime.utcnow().replace(hour=17, minute=0, second=0, microsecond=0)
    return [base + timedelta(minutes=rand) for rand in sorted(random.sample(range(60*5), n))]

def main():
    youtube = get_authenticated_service()

    uploaded = read_uploaded_log()
    videos = sorted(os.listdir("videos"))
    to_upload = []

    # اختيار 3 فيديوهات جديدة فقط
    for file in videos:
        if not file.lower().endswith(".mp4"):
            continue
        title = os.path.splitext(file)[0]
        if title not in uploaded:
            to_upload.append((file, title))
        if len(to_upload) == 3:
            break

    if not to_upload:
        print("✅ No new videos to upload.")
        return

    publish_times = generate_best_times(len(to_upload))

    for i, (file, title) in enumerate(to_upload):
        file_path = os.path.join("videos", file)
        publish_time = publish_times[i]
        description = "تلاوة قرآنية مباركة بصوت ندي"

        print(f"🚀 Uploading: {title} | Scheduled at {publish_time}")
        upload_video(youtube, file_path, title, description, publish_time)
        append_to_log(title)

if __name__ == "__main__":
    main()
