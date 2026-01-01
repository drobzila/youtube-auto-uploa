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
    "استمتع بسكينة القرآن", "عِش راحة القرآن", "لحظة مع كلام الله", "جمال التلاوة", "نور قلبك بالقرآن",
    "همسات قرآنية", "ترتيل يشرح الصدر", "أنفاس قرآنية", "رحلة مع القرآن", "معاني تطمئن القلب",
    "روعة الصوت القرآني", "طمأنينة من السماء", "قرآن يهز المشاعر", "صوت الملائكة",
    "صفاء النفس بالقرآن", "ترانيم الرحمة", "آيات تلين القلوب", "نور بين السطور", "سكون القلب",
    "قرآن الشفاء", "خُشوع لا يُوصف", "صوت يحيي الأرواح", "صدى الجنة", "بصوت من الجنة",
    "عيش القرآن بجوارحك", "هدوء القرآن", "نفحات قرآنية", "إيمان متجدد", "تلاوة تذيب القلوب",
    "صوت يهز الوجدان", "لحظة روحانية", "القرآن كما لم تسمعه من قبل", "سافر مع القرآن", "تأمل آية",
    "حديث الله إليك", "بوح السماء", "قرآن ينير الدرب", "صوت يرقى بالروح", "لحن الرحمة",
    "ركن الهدوء", "أنفاس السكينة", "نبض التلاوة", "فيض القرآن", "القرآن حياة", "ذِكر طيب",
    "أصوات من الجنة", "نور التلاوة", "رحمة القرآن", "مرفأ الطمأنينة", "سُطور نورانية",
    "طيف من الجنة", "السكينة في التلاوة", "بوح من السماء", "صفحة من نور", "عبق القرآن",
    "صوت الإيمان", "تلاوة تهدئ القلب", "آية تغير الحياة", "أمان الروح", "صوت يلامس القلب",
    "من أعماق الإيمان", "كلام الله يصل الأعماق", "هُدى ونور", "ارتقاء بالقرآن", "صوت يطهر القلب",
    "لحظة مع الإيمان", "في حضرة القرآن", "أنغام السماء", "آيات تلامس الأرواح", "خشوع لا يُضاهى",
    "جمال من الجنة", "صوت ينقلك لعالم آخر", "نورك في القرآن", "شوق للآيات", "بوح الإيمان",
    "نقاء التلاوة", "عذوبة القرآن", "صوت يحملك للسكينة", "مرفأ الإيمان", "القرآن طمأنينة",
    "هُدى الرحمن", "دقائق مع الله", "لحظات إيمانية", "ترتيل من القلب", "نور الروح",
    "ترانيم إيمانية", "صوت هادئ ونقي", "عبادة بالصوت", "أنفاس الإيمان", "همس التلاوة",
    "لحظة نقاء", "فيض نوراني", "آيات تتغلغل في القلب", "ترتيل مطمئن", "صوت مريح للنفس",
    "رحلة سماوية", "بوح الآيات", "دعاء يتلى", "القرآن رفيقك", "صوت يتسلل إلى روحك"
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

تلاوة قصيرة من القرآن الكريم 🌿 #قرآن #Quran #تلاوة
"""
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": ["قرآن", "Quran", "تلاوة", "راحة", "إيمان"],
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
