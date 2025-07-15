import os
import pickle
import datetime
import time
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def authenticate():
    creds = None
    if os.path.exists("token_upload.pickle"):
        with open("token_upload.pickle", "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token_upload.pickle", "wb") as token:
            pickle.dump(creds, token)
    return build("youtube", "v3", credentials=creds)

def get_video_files_from_folder(folder_path):
    return sorted([f for f in os.listdir(folder_path) if f.lower().endswith(".mp4")])

def generate_schedule_times(start_date, total_videos, times_per_day):
    schedule = []
    current_date = start_date
    index = 0
    for day in range((total_videos + len(times_per_day) - 1) // len(times_per_day)):
        for t in times_per_day:
            if index >= total_videos:
                break
            dt = datetime.datetime.strptime(f"{current_date} {t}", "%Y-%m-%d %H:%M")
            iso_time = dt.isoformat("T") + "Z"
            schedule.append(iso_time)
            index += 1
        current_date += datetime.timedelta(days=1)
    return schedule

def upload_and_schedule(folder, times_per_day, timezone_offset, videos_per_day):
    youtube = authenticate()
    files = get_video_files_from_folder(folder)
    total_files = len(files)
    if not files:
        print("📂 لا توجد فيديوهات mp4 في المجلد المحدد.")
        return

    schedule_times = generate_schedule_times(
        datetime.datetime.now(datetime.timezone.utc).date(), total_files, times_per_day
    )

    for i, filename in enumerate(files):
        video_path = os.path.join(folder, filename)
        title = os.path.splitext(filename)[0]
        publish_time = schedule_times[i]

        # تعديل التوقيت حسب المنطقة الزمنية
        dt_obj = datetime.datetime.strptime(publish_time, "%Y-%m-%dT%H:%M:%SZ")
        dt_obj += datetime.timedelta(hours=timezone_offset)
        publish_time = dt_obj.isoformat("T") + "Z"

        print(f"⬆️ رفع: {title}")
        request_body = {
            "snippet": {
                "title": title,
                "description": "",
                "categoryId": "22"
            },
            "status": {
                "privacyStatus": "private",
                "publishAt": publish_time,
                "selfDeclaredMadeForKids": False
            }
        }

        media_file = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/*")
        upload_request = youtube.videos().insert(
            part="snippet,status",
            body=request_body,
            media_body=media_file
        )

        start_time = time.time()
        response = None
        while response is None:
            status, response = upload_request.next_chunk()
            if status:
                elapsed = time.time() - start_time
                file_size = os.path.getsize(video_path)
                speed = (file_size / 1024 / 1024) / elapsed if elapsed > 0 else 0
                print(f"⚡ سرعة الرفع: {speed:.2f} MB/s")
        
        print(f"✅ تم جدولة: {title} في {publish_time}")
        time.sleep(1)

    print("🎉 تم رفع وجدولة كل الفيديوهات!")

if __name__ == "__main__":
    # حدد المجلد مباشرة في السكربت
    folder_path = "C:/Users/الاخوة ال4/Pictures/Music/Desktop/youtube-auto-uploa-main/videos"  # مثال للمجلد الذي يحتوي على الفيديوهات
    
    # حدد الأوقات مباشرة هنا
    times = ["08:00", "14:00", "20:00"]  # اختر الأوقات التي تريدها للنشر
    
    # اختر المنطقة الزمنية حسب حاجتك
    timezone_offset = 3  # مثال: المنطقة الزمنية UTC+3
    
    upload_and_schedule(folder_path, times, timezone_offset, 5)
