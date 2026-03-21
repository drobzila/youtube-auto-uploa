import os
import io
import random
import requests
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
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

# ================== Hooks ==================
hooks = [
    "نُهيّئ قلوبنا للقرآن",
    "القرآن جسر القلوب للجنة",
    "تلاوة تُصلح القلب",
    "سكينة وطمأنينة",
    "لا تُفوّت وقتك مع القرآن",
    "فرصة للتقرب إلى الله",
    "مع القرآن تحيا القلوب",
    "نعود للقرآن"
]

# ================== إعدادات Google Drive ==================
FOLDER_ID = os.environ.get("DRIVE_FOLDER_ID")
if not FOLDER_ID:
    raise RuntimeError("❌ DRIVE_FOLDER_ID غير موجود")

SCOPES = ["https://www.googleapis.com/auth/drive"]

creds = Credentials.from_authorized_user_info(
    info=eval(os.environ["GOOGLE_TOKEN"]),
    scopes=SCOPES
)

drive = build("drive", "v3", credentials=creds)

# ================== اختيار فيديو عشوائي ==================
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

# ================== كابشن تلغرام ==================
base_title = random.choice(hooks)

telegram_caption = (
    f"{base_title}\n"
    "🤍 تلاوة قصيرة تسعد القلب\n"
    "#قرآن #تلاوة"
)

# ================== رفع إلى تلغرام ==================
upload_to_telegram(video_name, telegram_caption)

# ================== حذف الفيديو ==================
drive.files().delete(fileId=video_id).execute()
os.remove(video_name)

print("🧹 تم حذف الفيديو من Drive والجهاز")
