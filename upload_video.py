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
            data={"chat_id": TELEGRAM_CHAT_ID, "caption": caption, "supports_streaming": True},
            files={"video": video_file}
        )
    if r.status_code == 200:
        print("📤 تم رفع الفيديو إلى تلغرام")
    else:
        print("❌ خطأ تلغرام:", r.text)

# ================== قائمة Hooks جاهزة ==================
hooks = [
    "قرآن يريح القلب 🤍", "تلاوة خاشعة تبعث السكينة", "آيات تهدئ النفس 🌿",
    "صوت يلامس الروح", "خشوع بلا حدود", "لحظة سكينة 🎧", "تلاوة مؤثرة",
    "نور القلب بالقرآن", "كلمات تطمئن القلب", "آرام القلوب بتلاوة القرآن",
    "صوت الملائكة 🤲", "عبق الإيمان", "تلاوة تهدئ المشاعر", "رحمة القرآن في صوت",
    "صفاء النفس مع القرآن", "أنغام السماء", "آرام الروح بالآيات", "لحظات خشوع",
    "تلاوة قصيرة تلمس القلب", "نور الروح بالقرآن"
]

# ================== إعدادات Google ==================
FOLDER_ID = os.environ.get("DRIVE_FOLDER_ID")
if not FOLDER_ID:
    raise RuntimeError("❌ متغير DRIVE_FOLDER_ID غير موجود")

SCOPES = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/youtube.upload"]

creds = Credentials.from_authorized_user_info(
    info=eval(os.environ["GOOGLE_TOKEN"]), scopes=SCOPES
)

drive = build("drive", "v3", credentials=creds)
youtube = build("youtube", "v3", credentials=creds)

# ================== جلب فيديوهات Drive ==================
results = drive.files().list(
    q=f"'{FOLDER_ID}' in parents and mimeType contains 'video/'",
    fields="files(id, name)"
).execute()

files = results.get("files", [])
if not files:
    print("❌ لا يوجد فيديوهات في Drive")
    exit()

video = random.choice(files)
video_id = video["id"]
video_name = video["name"]
print(f"🎬 اختيار الشورت: {video_name}")

# ================== تحميل الفيديو ==================
request = drive.files().get_media(fileId=video_id)
fh = io.FileIO(video_name, "wb")
downloader = MediaIoBaseDownload(fh, request)
done = False
while not done:
    status, done = downloader.next_chunk()
fh.close()
print("⬇️ تم تحميل الفيديو")

# ================== اختيار Hook ووصف ==================
title = random.choice(hooks) + " #Shorts"

descriptions = [
    f"{title}\n🤍 تلاوة قصيرة تبعث الطمأنينة\n#Shorts #Quran #قرآن",
    f"{title}\n🎧 استمع بخشوع\n#Shorts #تلاوة #Quran",
    f"{title}\n🌿 لحظة سكينة\n#Shorts #قرآن #Islam"
]

description = random.choice(descriptions)
tags = ["Shorts", "Quran", "قرآن", "تلاوة"]

# ================== رفع الفيديو إلى تلغرام ==================
telegram_caption = f"{title}\n🤍 تلاوة قصيرة\n#قرآن #Shorts"
upload_to_telegram(video_name, telegram_caption)

# ================== رفع الفيديو إلى يوتيوب ==================
media = MediaFileUpload(video_name, resumable=True)
youtube.videos().insert(
    part="snippet,status",
    body={
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "22"
        },
        "status": {"privacyStatus": "public"}
    },
    media_body=media
).execute()
print("✅ تم نشر الشورت بنجاح")

# ================== حذف الفيديو من Drive والجهاز ==================
drive.files().delete(fileId=video_id).execute()
os.remove(video_name)
print("🧹 تم الحذف والتنظيف")
