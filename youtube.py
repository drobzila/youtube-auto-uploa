import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# 🔐 إعداد الاعتماد باستخدام refresh_token
def get_drive_service():
    creds = Credentials(
        None,
        refresh_token="1//09z9fiYXnbgqYCgYIARAAGAkSNwF-L9Irb8Q9vZSSQtXff_tejyWZiMyQVXw5MVLj_M3MvUi5j5QsvDtTof9VJCJ1DtfnJWMkw70",
        token_uri="https://oauth2.googleapis.com/token",
        client_id="553805965519-1gvas0tmcl86v76k7m9bhkmc7m76657s.apps.googleusercontent.com",
        client_secret="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",
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    creds.refresh(Request())
    return build("drive", "v3", credentials=creds)

# 🗑️ حذف ملف من Google Drive حسب الاسم والمجلد
def delete_file_by_title(title, folder_id):
    service = get_drive_service()
    query = f"name = '{title}' and '{folder_id}' in parents"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])

    if not files:
        print(f"⚠️ لم يتم العثور على: {title}")
        return

    for file in files:
        try:
            service.files().delete(fileId=file['id']).execute()
            print(f"✅ تم حذف {file['name']}")
        except Exception as e:
            print(f"❌ فشل حذف {file['name']}: {e}")

# 📜 قراءة العناوين من log.txt (كل سطر فيه: العنوان - معرف - تاريخ)
def main():
    FOLDER_ID = '1_iPtcfFs3TpusMr9THwTc31SWtLtwccZ'  # ← ضع معرف المجلد الخاص بك
    with open('log.txt', 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split(' - ')
            if parts:
                title = parts[0].strip()
                if title:
                    delete_file_by_title(title, FOLDER_ID)

if __name__ == '__main__':
    main()
