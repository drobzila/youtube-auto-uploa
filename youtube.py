import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# بيانات OAuth 2.0
CLIENT_ID = "553805965519-1gvas0tmcl86v76k7m9bhkmc7m76657s.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REFRESH_TOKEN = "1//09z9fiYXnbgqYCgYIARAAGAkSNwF-L9Irb8Q9vZSSQtXff_tejyWZiMyQVXw5MVLj_M3MvUi5j5QsvDtTof9VJCJ1DtfnJWMkw70"
TOKEN_URI = "https://oauth2.googleapis.com/token"

FOLDER_ID = "1_iPtcfFs3TpusMr9THwTc31SWtLtwccZ"  # ✅ ضع هنا ID مجلد Google Drive الذي يحتوي الفيديوهات

def get_drive_service():
    creds = Credentials(
        None,
        refresh_token=REFRESH_TOKEN,
        token_uri=TOKEN_URI,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    creds.refresh(Request())
    return build("drive", "v3", credentials=creds)

def delete_file_by_title(title, folder_id):
    service = get_drive_service()
    query = f"name = '{title}' and '{folder_id}' in parents and trashed = false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get("files", [])
    if not files:
        print(f"⚠️ لم يتم العثور على: {title}")
        return
    for file in files:
        try:
            service.files().delete(fileId=file["id"]).execute()
            print(f"✅ تم حذف {file['name']}")
        except Exception as e:
            print(f"❌ فشل حذف {file['name']}: {e}")

def extract_titles_from_log(log_path):
    titles = []
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(" - Video ID:")
            if len(parts) >= 1:
                title = parts[0].strip()
                if title:
                    titles.append(title)
    return titles

def main():
    log_file = "log.txt"
    titles = extract_titles_from_log(log_file)
    for title in titles:
        delete_file_by_title(title, FOLDER_ID)

if __name__ == "__main__":
    main()
