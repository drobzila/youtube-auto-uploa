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

# ================== عناوين حسب نية المشاهد ==================
titles_by_intent = {
    "relax": [
        "قرآن يريح القلب 🤍 | تلاوة خاشعة",
        "Relaxing Quran Recitation | Calm & Peaceful",
        "تلاوة قرآنية هادئة تبعث الطمأنينة"
    ],
    "sleep": [
        "قرآن قبل النوم | تلاوة هادئة",
        "Quran for Sleep | Peaceful Recitation",
        "تلاوة قرآنية تساعد على النوم"
    ],
    "khushoo": [
        "تلاوة خاشعة مؤثرة من القرآن الكريم",
        "Beautiful Quran Recitation | Heart Touching",
        "قرآن يهز القلوب | تلاوة خاشعة"
    ]
}

intent = random.choice(list(titles_by_intent.keys()))
title = random.choice(titles_by_intent[intent])

# ================== أوصاف متغيرة ==================
descriptions = [
    f"""
{title}

🌿 تلاوة خاشعة من القرآن الكريم
🤍 تبعث الطمأنينة وراحة القلب
🎧 استمع بخشوع وشارك الأجر

🔍 كلمات يبحث عنها الناس:
قرآن يريح القلب
تلاوة خاشعة
Relaxing Quran
Quran for sleep

#قرآن #Quran #تلاوة_خاشعة #راحة_نفسية
""",

    f"""
{title}

🤲 لحظات إيمانية مع تلاوة قرآنية هادئة
🌙 مناسبة للراحة والتأمل قبل النوم

🔎 كلمات مفتاحية:
قرآن قبل النوم
Quran for sleep
تلاوة هادئة
Beautiful Quran

#Quran #Islam #تلاوة #طمأنينة
""",

    f"""
{title}

✨ استمع لتلاوة مؤثرة من القرآن الكريم
🤍 صوت يلامس القلب ويهدي النفس

📌 لا تنسَ الإعجاب والاشتراك دعمًا للمحتوى

#قرآن #تلاوة_هادئة #Quran #خشوع
"""
]

description = random.choice(descriptions)

# ================== وسوم متغيرة ==================
tags_pool = [
    ["قرآن", "Quran", "تلاوة خاشعة", "راحة نفسية"],
    ["Quran for sleep", "Relaxing Quran", "Islamic Recitation"],
    ["تلاوة هادئة", "قرآن يريح القلب", "خشوع"],
    ["Holy Quran", "Beautiful Quran", "Peaceful Recitation"]
]

tags = random.choice(tags_pool)

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
    print("❌ خطأ أثناء التحميل:", e)
    exit(1)

# ================== رفع إلى تلغرام ==================
telegram_caption = f"""{title}

🤍 تلاوة قرآنية تبعث السكينة
🌿 استمع وشارك الأجر

#قرآن #تلاوة #طمأنينة
"""
upload_to_telegram(video_name, telegram_caption)

# ================== رفع إلى يوتيوب ==================
try:
    media = MediaFileUpload(video_name, resumable=True)
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": "22"
            },
            "status": {
                "privacyStatus": "public"
            }
        },
        media_body=media
    )
    response = request.execute()
    print("✅ تم الرفع إلى يوتيوب:", response["id"])
except Exception as e:
    print("❌ خطأ رفع يوتيوب:", e)

# ================== حذف الفيديو ==================
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
