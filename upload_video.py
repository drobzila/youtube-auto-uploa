import os
import io
import random
import requests
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from google.oauth2.credentials import Credentials

# ================== إعدادات تلغرام ==================
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    raise RuntimeError("❌ متغيرات تلغرام غير مضافة في Secrets")

def upload_to_telegram(video_path, caption):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"

    with open(video_path, "rb") as video_file:
        r = requests.post(
            url,
            data={
                "chat_id": TELEGRAM_CHAT_ID,
                "caption": caption,
                "supports_streaming": True
            },
            files={"video": video_file}
        )

    if r.status_code == 200:
        print("📤 تم رفع الفيديو إلى تلغرام")
    else:
        print("❌ خطأ تلغرام:", r.text)

# ================== عناوين الفيديو ==================
# 📋 قائمة العناوين الجاهزة
video_titles = [
    "نصيحة من ذهب الحمد لله", "تذكر ", "اعمل الصالحات"
]
# ================== إعدادات Google ==================
FOLDER_ID = os.environ.get("DRIVE_FOLDER_ID")
if not FOLDER_ID:
    raise RuntimeError("❌ متغير DRIVE_FOLDER_ID غير موجود")

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/youtube.upload"
]

creds = Credentials.from_authorized_user_info(
    info=eval(os.environ["GOOGLE_TOKEN"]),
    scopes=SCOPES
)

drive = build("drive", "v3", credentials=creds)
youtube = build("youtube", "v3", credentials=creds)

# ================== جلب الفيديوهات ==================
results = drive.files().list(
    q=f"'{FOLDER_ID}' in parents and mimeType contains 'video/'",
    fields="files(id, name)"
).execute()

files = results.get("files", [])

if not files:
    print("❌ لا يوجد فيديوهات في Drive")
    exit()

# اختيار فيديو عشوائي
video = random.choice(files)
video_id = video["id"]
video_name = video["name"]
print(f"🎬 اختيار الفيديو: {video_name}")

# ================== تحميل الفيديو ==================
try:
    request = drive.files().get_media(fileId=video_id)
    fh = io.FileIO(video_name, "wb")
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()
    fh.close()
    print("⬇️ تم تحميل الفيديو")
except Exception as e:
    print("❌ خطأ أثناء تحميل الفيديو من Drive:", e)
    exit(1)

# ================== رفع الفيديو إلى تلغرام ==================
title = random.choice(video_titles)
telegram_caption = f"""{title}

🌿 تلاوة قرآنية خاشعة تبعث الطمأنينة
🤲 شارك الأجر ولا تنسَ الذكر

#قرآن #تلاوة_خاشعة #نسمات_القرآن
"""

upload_to_telegram(video_name, telegram_caption)

# ================== رفع الفيديو إلى يوتيوب ==================
try:
    media = MediaFileUpload(video_name, resumable=True)
    description = f"""

🔔 لا تنسَ الاشتراك وتفعيل الجرس
🤲 شارك المقطع لعلّه يكون سبب راحة لغيرك
"""
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "categoryId": "22"
            },
            "status": {"privacyStatus": "public"}
        },
        media_body=media
    )
    response = request.execute()
    print("✅ تم الرفع إلى يوتيوب:", response["id"])
except Exception as e:
    print("❌ خطأ أثناء رفع الفيديو إلى يوتيوب:", e)

# ================== حذف الفيديو من Drive والجهاز ==================
try:
    drive.files().delete(fileId=video_id).execute()
    print("🗑️ تم حذف الفيديو من Drive")
except Exception as e:
    print("⚠️ لم يتم حذف الفيديو من Drive:", e)

try:
    os.remove(video_name)
    print("🧹 تم حذف الملف المحلي")
except Exception as e:
    print("⚠️ لم يتم حذف الملف المحلي:", e)
