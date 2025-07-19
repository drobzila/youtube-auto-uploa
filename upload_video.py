import os
import pickle
import datetime
import random
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# إعدادات
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
FOLDER_PATH = "videos"
LOG_FILE = "log.txt"
DAILY_UPLOAD_COUNT = 3

# تحميل بيانات الاعتماد
def get_authenticated_service():
    creds = None
    if os.path.exists("token_upload.pickle"):
        with open("token_upload.pickle", "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
            creds = flow.run_console()
        with open("token_upload.pickle", "wb") as token:
            pickle.dump(creds, token)
    return build("youtube", "v3", credentials=creds)

# تسجيل الفيديوات المرفوعة
def save_to_log(video_title, video_id):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{video_id}|{video_title}\n")

def load_uploaded_videos():
    if not os.path.exists(LOG_FILE):
        return set()
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return set(line.strip().split("|")[1] for line in f.readlines())

# رفع فيديو
def upload_video(youtube, file_path, title, publish_time):
    print(f"🚀 Uploading: {title} | Scheduled at {publish_time}")
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "categoryId": "22"
            },
            "status": {
                "privacyStatus": "private",
                "publishAt": publish_time.isoformat(),
                "selfDeclaredMadeForKids": False
            }
        },
        media_body=MediaFileUpload(file_path, resumable=True)
    )
    response = None
    while response is None:
        status, response = request.next_chunk()
    video_id = response["id"]
    save_to_log(video_id, title)

# توليد أوقات النشر
def generate_publish_times(count):
    base = datetime.datetime.utcnow().replace(hour=16, minute=0, second=0, microsecond=0)
    if datetime.datetime.utcnow() > base:
        base += datetime.timedelta(days=1)
    return [base + datetime.timedelta(minutes=i * 30) for i in range(count)]

# البرنامج الرئيسي
def main():
    youtube = get_authenticated_service()
    uploaded_titles = load_uploaded_videos()

    all_videos = [f for f in os.listdir(FOLDER_PATH) if f.endswith(".mp4")]
    to_upload = []
    for f in all_videos:
        title = os.path.splitext(f)[0]
        if title not in uploaded_titles:
            to_upload.append((os.path.join(FOLDER_PATH, f), title))
        if len(to_upload) == DAILY_UPLOAD_COUNT:
            break

    if not to_upload:
        print("✅ No new videos to upload.")
        return

    publish_times = generate_publish_times(len(to_upload))

    for (file_path, title), publish_time in zip(to_upload, publish_times):
        upload_video(youtube, file_path, title, publish_time)

if __name__ == "__main__":
    main()
