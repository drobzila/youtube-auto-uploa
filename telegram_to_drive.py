import os
import asyncio
from telethon import TelegramClient
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# ===== إعدادات التلغرام =====
api_id = int(os.environ["TELEGRAM_API_ID"])
api_hash = os.environ["TELEGRAM_API_HASH"]
channel = os.environ["TELEGRAM_CHANNEL"]
download_dir = "downloads"
os.makedirs(download_dir, exist_ok=True)

# ===== بيانات Google OAuth =====
CLIENT_ID = os.environ["GOOGLE_CLIENT_ID"]
CLIENT_SECRET = os.environ["GOOGLE_CLIENT_SECRET"]
REFRESH_TOKEN = os.environ["GOOGLE_REFRESH_TOKEN"]
FOLDER_ID = os.environ["GOOGLE_FOLDER_ID"]

SCOPES = ["https://www.googleapis.com/auth/drive"]

creds = Credentials(
    None,
    refresh_token=REFRESH_TOKEN,
    token_uri="https://oauth2.googleapis.com/token",
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    scopes=SCOPES,
)
creds.refresh(Request())
drive_service = build("drive", "v3", credentials=creds)

# ===== تحميل الفيديوهات من التلغرام =====
async def download_videos():
    client = TelegramClient("session", api_id, api_hash)
    await client.start()

    async for message in client.iter_messages(channel, limit=20):
        if message.video and message.file.size <= 7 * 1024 * 1024:  # <= 7MB
            filename = message.file.name or f"{message.id}.mp4"
            filepath = os.path.join(download_dir, filename)

            print(f"⬇️ Downloading: {filename}")
            await message.download_media(file=filepath)
            print(f"✅ Saved locally: {filepath}")

            # رفع إلى Google Drive
            file_metadata = {
                "name": filename,
                "parents": [FOLDER_ID]
            }
            media = MediaFileUpload(filepath, resumable=True)
            drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields="id"
            ).execute()
            print(f"☁️ Uploaded to Drive: {filename}")

    await client.disconnect()

asyncio.run(download_videos())
