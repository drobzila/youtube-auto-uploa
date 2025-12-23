import os
import io
import random
import requests

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from google.oauth2.credentials import Credentials


# ================== إعدادات تلغرام ==================
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


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
            files={
                "video": video_file
            }
        )

    if r.status_code == 200:
        print("📤 تم رفع الفيديو إلى تلغرام")
    else:
        print("❌ خطأ تلغرام:", r.text)


# ================== عناوين الفيديو ==================
# 📋 قائمة العناوين الجاهزة
video_titles = [
    "تلاوة خاشعة تلامس القلوب", "صوت يريح القلب والعقل", "آيات تبعث الطمأنينة في النفس",
    "تلاوة عذبة تدمع لها العيون", "استمع لتلاوة تهز المشاعر", "أجمل تلاوة قرآنية مؤثرة جدًا",
    "تلاوة نادرة تبكي القلوب", "صوت ملائكي يشرح الصدر", "خشوع لا يُوصف أثناء التلاوة",
    "تلاوة تهز الوجدان بخشوعها", "صوت يأخذك إلى عالم من السكينة", "أجمل ما تسمع من القرآن الكريم",
    "لحظات روحانية لا تُنسى مع القرآن", "تلاوة تملأ القلب بالنور", "صوت يذكرك بالجنة",
    "راحة نفسية لا توصف مع هذه التلاوة", "آيات تشرح الصدر وتُذهب الهم", "جمال الترتيل وروعة الأداء",
    "صوت يدخل القلب بدون استئذان", "تلاوة هادئة قبل النوم تبعث السكينة",
    "ترتيل يبكي الصخر من الخشوع", "تلاوة مؤثرة بصوت نادر الجمال", "قرآن يلامس الإحساس بعمق",
    "استمع بقلبك لا بأذنك", "تلاوة هادئة تريح أعصابك وتملأك إيمانًا",
    "خشوع لا مثيل له في هذه التلاوة", "صوت كأنه من السماء", "آيات من نور تملأ المكان طمأنينة",
    "تلاوة تذكرك بلقاء الله", "صوت يبكي المستمعين بخشوعه", "لحظة صفاء مع كلام الله",
    "استمع لتلاوة تجعلك تبكي من الخشوع", "تلاوة نادرة من المسجد الحرام", "ترتيل مؤثر من قلب صادق",
    "صوت يبعث السكينة في كل من يسمع", "القرآن شفاء للقلوب — تلاوة مؤثرة جدًا",
    "تلاوة تبعث الطمأنينة في ليل هادئ", "ترتيل ملائكي يلامس الأرواح", "تلاوة من أروع ما يكون",
    "صوت يدخل القلب بلا مقدمات", "قرآن يُتلى بخشوع نادر", "استمع لهذه التلاوة وستشعر بالسكينة",
    "ترتيل يبعث الدموع من شدة الخشوع", "تلاوة تهدئ القلب المرهق", "جمال الصوت وروعة الأداء القرآني",
    "آيات تبكيك من جمالها", "تلاوة مؤثرة جدًا بصوت رائع", "لحظة مع كلام الله تبعث الطمأنينة",
    "صوت مؤثر يذكّرك بالآخرة", "القرآن الكريم بصوت يريح النفس",
    "استمع إلى أجمل ما قرئ من كتاب الله", "صوت نادر في تلاوة تبكي الحجر",
    "تلاوة خاشعة تلامس الروح", "صوت يملأ المكان نورًا وطمأنينة", "ترتيل عذب يهز المشاعر"
]

# ================== إعدادات Google ==================
FOLDER_ID = "1lLKbFPovufWeEkwpCgI3cM-Je-Uee9el"

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
    print("❌ لا يوجد فيديوهات")
    exit()

video = random.choice(files)
print(f"🎬 اختيار الفيديو: {video['name']}")


# ================== تحميل الفيديو ==================
request = drive.files().get_media(fileId=video["id"])
fh = io.FileIO(video["name"], "wb")
downloader = MediaIoBaseDownload(fh, request)

done = False
while not done:
    status, done = downloader.next_chunk()

fh.close()
print("⬇️ تم تحميل الفيديو")


# ================== النشر في تلغرام ==================
title = random.choice(video_titles)

telegram_caption = f"""{title}

🌿 تلاوة قرآنية خاشعة تبعث الطمأنينة
🤲 شارك الأجر ولا تنسَ الذكر

#قرآن #تلاوة_خاشعة #نسمات_القرآن
"""

upload_to_telegram(video["name"], telegram_caption)


# ================== الرفع إلى يوتيوب ==================
media = MediaFileUpload(video["name"], resumable=True)

description = """
تلاوة قرآنية خاشعة تملأ القلب طمأنينة 🌿
استمع بخشوع لآيات من كلام الله بصوت مؤثر يريح النفس ويبعث السكينة.

🔔 لا تنسَ الاشتراك وتفعيل الجرس
🤲 شارك المقطع لعلّه يكون سبب راحة لغيرك

#قرآن #تلاوة_خاشعة #راحة_نفسية #القرآن_الكريم #تلاوة_مؤثرة
"""

request = youtube.videos().insert(
    part="snippet,status",
    body={
        "snippet": {
            "title": title,
            "description": description,
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


# ================== تنظيف ==================
drive.files().delete(fileId=video["id"]).execute()
print("🗑️ تم حذف الفيديو من Drive")

os.remove(video["name"])
print("🧹 تم حذف الملف المحلي")
print(f"🎬 اختيار الفيديو: {video['name']}")

# ⬇️ تحميل الفيديو مؤقتاً
request = drive.files().get_media(fileId=video["id"])
fh = io.FileIO(video["name"], "wb")
downloader = MediaIoBaseDownload(fh, request)

done = False
while not done:
    status, done = downloader.next_chunk()

fh.close()

# ⬆️ رفعه إلى يوتيوب
media = MediaFileUpload(video["name"], resumable=True)

title = random.choice(video_titles)

description = """
تلاوة قرآنية خاشعة تملأ القلب طمأنينة 🌿
استمع بخشوع لآيات من كلام الله بصوت مؤثر يريح النفس ويبعث السكينة.

🔔 لا تنسَ الاشتراك وتفعيل الجرس
🤲 شارك المقطع لعلّه يكون سبب راحة لغيرك

#قرآن #تلاوة_خاشعة #راحة_نفسية #القرآن_الكريم #تلاوة_مؤثرة
"""

request = youtube.videos().insert(
    part="snippet,status",
    body={
        "snippet": {
            "title": title,
            "description": description,
            "categoryId": "22"
        },
        "status": {
            "privacyStatus": "public"
        }
    },
    media_body=media
)

response = request.execute()
print("✅ تم الرفع:", response["id"])

# 🗑️ حذف الفيديو من Drive
drive.files().delete(fileId=video["id"]).execute()
print("🗑️ تم حذف الفيديو من Drive")

os.remove(video["name"])
