import os
import io
import random
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from google.oauth2.credentials import Credentials

FOLDER_ID = os.environ["1lLKbFPovufWeEkwpCgI3cM-Je-Uee9el"]

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/youtube.upload"
]

# تحميل التوكن من Secrets
creds = Credentials.from_authorized_user_info(
    info=eval(os.environ["GOOGLE_TOKEN"]),
    scopes=SCOPES
)

drive = build("drive", "v3", credentials=creds)
youtube = build("youtube", "v3", credentials=creds)

# 🔍 جلب الفيديوهات من المجلد
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

request = youtube.videos().insert(
    part="snippet,status",
    body={
        "snippet": {
            "title": video["name"],
            "description": "تم الرفع تلقائياً",
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
