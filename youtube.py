from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os

SCOPES = ['https://www.googleapis.com/auth/drive']
FOLDER_ID = '1_iPtcfFs3TpusMr9THwTc31SWtLtwccZ'  # ✅ ضع هنا معرف مجلد Google Drive

# مصادقة الوصول إلى Google Drive
def get_drive_service():
    creds = None
    if os.path.exists('token_oauth.json'):
        creds = Credentials.from_authorized_user_file('token_oauth.json', SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token_oauth.json', 'w') as token:
            token.write(creds.to_json())
    return build('drive', 'v3', credentials=creds)

# حذف ملف من درايف بناءً على العنوان والمجلد
def delete_file_by_title(title, folder_id):
    service = get_drive_service()
    query = f"name = '{title}' and '{folder_id}' in parents and trashed = false"
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

# استخراج العناوين من log.txt
def extract_titles_from_log(log_file):
    titles = set()
    with open(log_file, 'r', encoding='utf-8') as f:
        for line in f:
            if " - Video ID:" in line:
                title = line.split(" - Video ID:")[0].strip()
                titles.add(title)
    return titles

def main():
    titles = extract_titles_from_log("log.txt")
    for title in titles:
        delete_file_by_title(title, FOLDER_ID)

if __name__ == '__main__':
    main()
