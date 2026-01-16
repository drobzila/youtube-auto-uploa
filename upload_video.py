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
    if r.ok:
        print("📤 تم رفع الفيديو إلى تلغرام")
    else:
        print("❌ خطأ تلغرام:", r.text)

# ================== Hooks (عناوين جذابة) ==================
hooks = [
    "شعبان… والقلوب تستعد لرمضان 🤍",
    "في شعبان نُهيّئ قلوبنا لرمضان",
    "شعبان جسر القلوب إلى رمضان",
    "تلاوة تُصلح القلب قبل رمضان",
    "من شعبان يبدأ الطريق إلى رمضان",
    "تلاوة في شعبان تفتح لك رمضان",
    "شعبان… لا تُفوّت الاستعداد",
    "شعبان فرصة قبل رمضان",
    "شعبان تهيئة، ورمضان حياة",
    "في شعبان نعود للقرآن قبل رمضان"
]

# ================== إعدادات Google ==================
FOLDER_ID = os.environ.get("DRIVE_FOLDER_ID")
if not FOLDER_ID:
    raise RuntimeError("❌ DRIVE_FOLDER_ID غير موجود")

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

# ================== جلب فيديو عشوائي ==================
results = drive.files().list(
    q=f"'{FOLDER_ID}' in parents and mimeType contains 'video/'",
    fields="files(id, name)"
).execute()

files = results.get("files", [])
if not files:
    raise RuntimeError("❌ لا يوجد فيديوهات في Google Drive")

video = random.choice(files)
video_id = video["id"]
video_name = video["name"]

print(f"🎬 تم اختيار: {video_name}")

# ================== تحميل الفيديو ==================
request = drive.files().get_media(fileId=video_id)
fh = io.FileIO(video_name, "wb")
downloader = MediaIoBaseDownload(fh, request)

done = False
while not done:
    status, done = downloader.next_chunk()

fh.close()
print("⬇️ تم تحميل الفيديو")

# ================== العنوان والوصف ==================
base_title = random.choice(hooks)  # عناوين شعبان الموصلة لرمضان
title = f"{base_title} #Shorts"

description = (
    f"{base_title}\n\n"
    "🤍 تلاوة قصيرة في شعبان تهيّئ القلب لرمضان\n"
    "📖 القرآن نور القلوب وراحة النفوس\n\n"
    "#Shorts #Quran #قرآن #شعبان #رمضان #تلاوة #Islam"
)

tags = [
    "Shorts", "Quran", "قرآن", "تلاوة",
    "Islam", "QuranShorts", "شعبان",
    "Ramadan", "تهيئة_رمضان", "تلاوة_خاشعة"
]

# ================== رفع إلى تلغرام ==================
telegram_caption = (
    f"{base_title}\n"
    "🤍 تلاوة قصيرة تهيّئ القلب لرمضان\n"
    "#قرآن #شعبان #رمضان"
)

upload_to_telegram(video_name, telegram_caption)

# ================== رفع إلى يوتيوب (غير مخصص للأطفال) ==================
media = MediaFileUpload(video_name, resumable=True)

youtube.videos().insert(
    part="snippet,status",
    body={
        "snippet": {
            "title": title[:100],  # أمان
            "description": description,
            "tags": tags,
            "categoryId": "22"
        },
        "status": {
            "privacyStatus": "public",
            "madeForKids": False,
            "selfDeclaredMadeForKids": False
        }
    },
    media_body=media
).execute()

print("✅ تم نشر الشورت بنجاح (غير مخصص للأطفال)")

# ================== تنظيف ==================
drive.files().delete(fileId=video_id).execute()
os.remove(video_name)

print("🧹 تم حذف الفيديو من Drive والجهاز")
