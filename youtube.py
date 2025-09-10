from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# بيانات OAuth
CLIENT_ID = "553805965519-1gvas0tmcl86v76k7m9bhkmc7m76657s.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REFRESH_TOKEN = "1//09SLS4A1oZYsJCgYIARAAGAkSNwF-L9IrQJneNmOVOAjihJWVMGFL2gYlLAdg0Y_0SZg4bQPjbRR-qkDKYvbSS4weE7zrPh8w4_E"

SCOPES = ["https://www.googleapis.com/auth/drive"]
FOLDER_ID = "1_iPtcfFs3TpusMr9THwTc31SWtLtwccZ"

def get_drive_service():
    creds = Credentials(
        None,
        refresh_token=REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scopes=SCOPES
    )
    creds.refresh(Request())
    return build('drive', 'v3', credentials=creds)

def delete_file_by_title(service, title, folder_id):
    # التأكد من أن علامات الاقتباس لا تسبب مشاكل
    title_safe = title.replace("'", "\\'")
    query = f"name = '{title_safe}' and '{folder_id}' in parents"

    page_token = None
    deleted = False
    while True:
        results = service.files().list(
            q=query,
            fields="nextPageToken, files(id, name)",
            pageToken=page_token
        ).execute()
        files = results.get('files', [])
        for file in files:
            try:
                service.files().delete(fileId=file['id']).execute()
                print(f"✅ تم حذف: {file['name']}")
                deleted = True
            except Exception as e:
                print(f"❌ فشل حذف {file['name']}: {e}")
        page_token = results.get('nextPageToken', None)
        if page_token is None:
            break
    if not deleted:
        print(f"⚠️ لم يتم العثور على: {title}")

def main():
    service = get_drive_service()
    with open("log.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        if " - Video ID:" in line:
            title = line.split(" - Video ID:")[0].strip()
            delete_file_by_title(service, title, FOLDER_ID)

if __name__ == "__main__":
    main()
