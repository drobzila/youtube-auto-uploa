import os
import io
import json
import random
import hashlib
import datetime
import subprocess
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from google.auth.transport.requests import Request

# ------------------ إعدادات ------------------
FOLDER_ID = "1lLKbFPovufWeEkwpCgI3cM-Je-Uee9el"
TIMEZONE_OFFSET = 1  # الجزائر +1
WINDOW_MINUTES = 10   # نافذة زمنية للنشر
JSON_FILE = "uploaded.json"

video_titles = [
    "تلاوة خاشعة تلامس القلوب", "صوت يريح القلب والعقل", 
    "آيات تبعث الطمأنينة في النفس", "تلاوة عذبة تدمع لها العيون"
]

# ------------------ إنشاء أو تحميل uploaded.json ------------------
if not os.path.exists(JSON_FILE):
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump({"videos": []}, f, ensure_ascii=False, indent=2)

with open(JSON_FILE, "r", encoding="utf-8") as f:
    uploaded_data = json.load(f)  # ✅ اسم متغير ثابت

def is_uploaded(file_hash):
    return file_hash in uploaded_data["videos"]

def mark_uploaded(file_hash):
    uploaded_data["videos"].append(file_hash)
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(uploaded_data, f, ensure_ascii=False, indent=4)

# ------------------ خدمات Google ------------------
def get_drive_service():
    credentials = ServiceAccountCredentials.from_service_account_info(
        {
  "type": "service_account",
  "project_id": "quran-478116",
  "private_key_id": "9afa7d003241409eab8c46514cdb1bdcebe192fe",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC61sax194Qban3\nCBDZfkdpahT7fRKMIDC2Jd42wzCV9BeLwUyxKDqkTbpT59fmvT9L7b++IHsx+Af0\nUCi9BSZQ2cRhpY0LueaMBxZ2Ov++HosL5bOIHhvAUByAqwUslSAVTtvdKgWNCP7Q\nlifyuPcuYhtk6jlBtTsz9OknN5/DobxC6PW/7Z1kQcTfgxGt9eRiXIGcjMdIzMAu\n/yJX/38bt6khxaCZiYF94rrMzOJI7NnXjexEeh0JmW6rDbnQhCgsQ4r2mOPYxq3f\nhAVcfarV8M4qC0yrpwOQg+n7jonw8e0lZRc+y1cjtyKcHc7rqCw0LmKpdhwaV4Cj\nJn3mPgctAgMBAAECggEAPJmZ86fxAkIXfSTUFj8TmXjLWnCMOf/c3M92fiucEB8O\nHgmxvsouDwmY9Er/53qdU5rG9LtjSedJaTAwrnJDpbikLgm8sD95LBTGb82eEoOk\nlNTJgM5HMP6q5/7QXE/4CoE75cWR7FctEumJBnyAy74NZZNkw8+s5qK6lro/avt2\nDdc/piaHDZElmgslokRHFG0609GRfEYeKZUM9nNOL42Ni+DOBW4y/TZyw7EbV8OY\n8TFRH6OjCCw5Mdi2E3c6tsqR8hERb2HqYg7Yn8swFt4X5hYigQEIC7kkbLIqToNL\nsri78pxYHedVO2qpVa6NQO13QXuO2Myyt1kEbUMm/wKBgQDa1oDMF/KoNQYlgARV\nDWe1ORRiitdtv1QeON/50TwSKfnNJR3+8Ya4k3u1DhfEPIyei7BZVbrBIphHDULh\n+nthhIUTr6kmt9qLyfwvdIizzK1kZrYsWz9QfoJwCzXNyBp6StJCovxeFbAxDOaO\n38o+TJrnqx7HerUxnlW6o9c89wKBgQDakTCSFFgu3XfQNOUH9y2uuOOj8vysSGx4\nOQIPm9FoAhsP0owEaL0Evf5E+hzswaEhgguo/yEeeK2X6HA2LPvYY40OHNnKKojp\nHP0cnG3bmD1143a+hSw17K/mFAk8lPjIPC+Y2ey5KWVzzKyoc8dM838TpmJ0ZU0n\n4iC0DqmH+wKBgCEsqWPHMZr8Rs1CheWa3aDkYUm7AIN7oLXgK1wEsxWR1XOa79wp\nIyIyAWvmEgZGo46ZYId6bpA+vVTwFraJMVEMNNxSIdNjxbaxTRComtye554zz+QT\nhRqfwwhXOrXSYuktFIjTimx83zPgX8dC97bQCB+cmlLlMDiwZxCfK87rAoGBAJdz\nK9jNSB2RUMhxHpLacEk1zGd6pCMtPBxCRG9UZVJQwze/iU401WVH0b0yIoDb2y9A\n0ZuUzfozXPZ6Fec0XH6g3Mj+rNsthhkiATGmI2maoFvj9hAmb3AeRfSDxbK493qo\nWcLsnt/fE3GeTbWcJGnqABA5ptdIqqIMSuT5k/epAoGBAMf77nLW5iZHxYB8bjVp\n2cWbtnvH/yMRRRNdeWSkV/RZDOGKWcGBSRER/HbbW5Ti9Jr3qi6CDjGiiXXiX0EX\nnhVWrJ+EXx4SDKGDpCUt/g5a7874FTpJCj/l192MTmBbr0I8G24rrhnLzGuJMIEC\neUYV6/SM0xYTOKBZSKJ4aETw\n-----END PRIVATE KEY-----\n",
  "client_email": "quran-833@quran-478116.iam.gserviceaccount.com",
  "client_id": "115882713836588740161",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/quran-833%40quran-478116.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
},
        scopes=["https://www.googleapis.com/auth/drive"]
    )
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

# ------------------ تحميل الفيديو من Drive ------------------
def download_video_from_drive(file_id, file_name, drive_service):
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.FileIO(file_name, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    return file_name

def file_hash(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

# ------------------ رفع الفيديو على YouTube ------------------
def upload_video_to_youtube(file_path, title, youtube_service):
    body = {
        "snippet": {
            "title": title,
            "description": "✨ استمع إلى تلاوة خاشعة مؤثرة من القرآن الكريم 🌿",
            "tags": ["قرآن", "تلاوة", "Quran", "خشوع"]
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }
    media = MediaFileUpload(file_path, mimetype="video/*", resumable=True)
    request = youtube_service.videos().insert(part="snippet,status", body=body, media_body=media)
    response = request.execute()
    print(f"✅ Uploaded: {title} | ID: {response['id']}")
    mark_uploaded(file_hash(file_path))

# ------------------ اختيار عنوان فريد ------------------
def make_unique_title():
    while True:
        t = random.choice(video_titles)
        if t not in [v for v in uploaded_data["videos"]]:
            return t

# ------------------ التحقق من وقت النشر ------------------
def is_time_to_upload(schedule_hours, tz, window_minutes):
    now = datetime.datetime.now(tz)
    for h in schedule_hours:
        start = datetime.datetime.combine(now.date(), datetime.time(h, 0, tzinfo=tz))
        end = start + datetime.timedelta(minutes=window_minutes)
        if start <= now < end:
            return True
    return False

# ------------------ Git Push ------------------
def push_uploaded_json():
    try:
        subprocess.run(["git", "pull", "--rebase"], check=False)
        subprocess.run(["git", "add", JSON_FILE], check=True)
        subprocess.run(["git", "commit", "-m", "🪶 تحديث سجل الفيديوهات"], check=False)
        subprocess.run(["git", "push"], check=True)
        print(f"✅ {JSON_FILE} pushed to GitHub.")
    except Exception as e:
        print(f"❌ Push failed: {e}")


# التأكد من وجود الملف وصلاحيته
if not os.path.exists(JSON_FILE):
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump({"videos": []}, f, ensure_ascii=False, indent=2)

# محاولة قراءة JSON، وإن فشل إنشاء جديد
try:
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        content = f.read().strip()
        if content:
            uploaded_data = json.loads(content)
        else:
            raise ValueError("Empty file")
except (json.JSONDecodeError, ValueError):
    uploaded_data = {"videos": []}
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(uploaded_data, f, ensure_ascii=False, indent=2)

# ------------------ Main ------------------
def main():
    tz = datetime.timezone(datetime.timedelta(hours=TIMEZONE_OFFSET))
    schedule_hours = list(range(24))  # كل ساعة

    if not is_time_to_upload(schedule_hours, tz, WINDOW_MINUTES):
        print("⏸ ليس وقت الرفع، الخروج.")
        return

    drive_service = get_drive_service()
    youtube_service = get_youtube_service()

    files = drive_service.files().list(
        q=f"'{FOLDER_ID}' in parents and mimeType contains 'video/'",
        fields="files(id, name)"
    ).execute().get("files", [])

    if not files:
        print("⚠️ لا توجد فيديوهات في المجلد.")
        return

    random.shuffle(files)
    for file in files:
        path = download_video_from_drive(file["id"], file["name"], drive_service)
        h = file_hash(path)
        if is_uploaded(h):
            print(f"❗ الفيديو {file['name']} تم رفعه مسبقًا، تخطي.")
            os.remove(path)
            continue
        title = make_unique_title()
        upload_video_to_youtube(path, title, youtube_service)
        os.remove(path)
        print(f"🧹 حذف {file['name']} بعد الرفع")
        break  # رفع فيديو واحد لكل نافذة زمنية

    push_uploaded_json()
    print("🏁 Done!")

if __name__ == "__main__":
    main()
