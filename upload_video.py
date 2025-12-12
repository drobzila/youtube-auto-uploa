import os
import random
import json
import time
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
import io

# -----------------------------
# إعدادات ثابتة
# -----------------------------
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")
SERVICE_ACCOUNT_FILE = "service_account.json"

# -----------------------------
# خدمة Google Drive عبر Service Account
# -----------------------------
def get_drive_service():
    creds = ServiceAccountCredentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    return build("drive", "v3", credentials=creds)

# -----------------------------
# خدمة YouTube عبر OAuth Refresh Token
# -----------------------------
def get_youtube_service():
    creds = Credentials(
        None,
        refresh_token=os.getenv("YOUTUBE_REFRESH_TOKEN"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("YOUTUBE_CLIENT_ID"),
        client_secret=os.getenv("YOUTUBE_CLIENT_SECRET")
    )
    creds.refresh(Request())
    return build("youtube", "v3", credentials=creds)

# -----------------------------
# اختيار فيديو عشوائي من Drive
# -----------------------------
def pick_random_video(drive):
    query = f"'{DRIVE_FOLDER_ID}' in parents and mimeType contains 'video/'"
    results = drive.files().list(q=query, fields="files(id, name)").execute()
    files = results.get("files", [])

    if not files:
        print("❌ لا توجد فيديوهات في المجلد!")
        return None

    return random.choice(files)

# -----------------------------
# تنزيل الفيديو من Drive
# -----------------------------
def download_from_drive(drive, file_id, file_name):
    request = drive.files().get_media(fileId=file_id)
    fh = io.FileIO(file_name, "wb")
    downloader = MediaIoBaseDownload(fh, request)

    print(f"⬇️ جاري تنزيل: {file_name}")
    done = False
    while not done:
        status, done = downloader.next_chunk()
    print("✅ تم التنزيل")

# -----------------------------
# رفع الفيديو إلى YouTube
# -----------------------------
def upload_to_youtube(youtube, file_path, title):
    print("📤 رفع الفيديو إلى YouTube ...")

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {"title": title},
            "status": {"privacyStatus": "public"}
        },
        media_body=MediaFileUpload(file_path, chunksize=-1, resumable=True)
    )

    response = None
    while response is None:
        status, response = request.next_chunk()

    print("🎉 تم رفع الفيديو بنجاح!")
    print("🔗 Video ID:", response.get("id"))

# -----------------------------
# حذف الفيديو من Google Drive
# -----------------------------
def delete_from_drive(drive, file_id):
    drive.files().delete(fileId=file_id).execute()
    print("🗑️ تم حذف الفيديو من Drive")

# -----------------------------
# حفظ اسم الفيديو في سجل
# -----------------------------
def log_video(name):
    with open("log.txt", "a", encoding="utf-8") as f:
        f.write(name + "\n")

# -----------------------------
# العملية الرئيسية
# -----------------------------
def main():
    print("🚀 بدء العملية...")

    drive = get_drive_service()
    youtube = get_youtube_service()

    file = pick_random_video(drive)
    if not file:
        return

    file_id = file["id"]
    file_name = file["name"]

    download_from_drive(drive, file_id, file_name)
    upload_to_youtube(youtube, file_name, file_name)

    delete_from_drive(drive, file_id)
    log_video(file_name)

    os.remove(file_name)

    print("✨ العملية اكتملت بنجاح!")


if __name__ == "__main__":
    main()
