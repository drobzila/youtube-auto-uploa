import os
import pickle
import random
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.pickle"
LOG_FILE = "log.txt"
VIDEO_FOLDER = "videos"  # مجلد الفيديوهات داخل Google Drive

# أوقات الذروة لليوتيوب حسب التوقيت المحلي (UTC+1)
PEAK_TIMES = [
    (12, 0),  # 12:00 ظهرًا
    (18, 0),  # 18:00 مساءً
    (21, 0)   # 21:00 مساءً
]

def authenticate():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    return build('youtube', 'v3', credentials=creds)

def load_uploaded_titles():
    if not os.path.exists(LOG_FILE):
        return set()
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        return set(line.strip() for line in f)

def save_uploaded_title(title):
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(title + '\n')

def get_videos_to_upload():
    all_files = [f for f in os.listdir(VIDEO_FOLDER) if f.endswith(('.mp4', '.mov', '.avi'))]
    uploaded_titles = load_uploaded_titles()
    return [f for f in all_files if f not in uploaded_titles][:3]

def get_schedule_time(index):
    now = datetime.utcnow() + timedelta(hours=1)  # الجزائر UTC+1
    today = now.date()
    hour, minute = PEAK_TIMES[index % len(PEAK_TIMES)]
    schedule_time = datetime(today.year, today.month, today.day, hour, minute)
    if schedule_time < now:
        schedule_time += timedelta(days=1)  # إذا فات الوقت المجدول، اجل للغد
    return schedule_time.isoformat("T") + ".000Z"

def upload_video(youtube, file_name, schedule_time):
    title = os.path.splitext(file_name)[0]
    video_path = os.path.join(VIDEO_FOLDER, file_name)

    body = {
        'snippet': {
            'title': title,
            'description': 'تم الرفع تلقائيًا',
            'tags': ['قرآن', 'تلاوة', 'اسلام'],
            'categoryId': '27'
        },
        'status': {
            'privacyStatus': 'private',
            'publishAt': schedule_time,
            'selfDeclaredMadeForKids': True
        }
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part=','.join(body.keys()), body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Progress: {int(status.progress() * 100)}%")

    print(f"✅ تم رفع الفيديو: {title} في {schedule_time}")
    save_uploaded_title(file_name)

def main():
    youtube = authenticate()
    videos = get_videos_to_upload()

    if not videos:
        print("🚫 لا يوجد فيديوهات جديدة للرفع.")
        return

    for index, video in enumerate(videos):
        schedule_time = get_schedule_time(index)
        upload_video(youtube, video, schedule_time)

if __name__ == '__main__':
    main()
