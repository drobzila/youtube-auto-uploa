from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# 🔐 بيانات OAuth (كما هي — لم تُمس)
CLIENT_ID = "108880269998-29mupf5siumdovf83irg7ocqgkd8q21n.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REFRESH_TOKEN = "1//04eSUNf4_LX0MCgYIARAAGAQSNwF-L9IrcxJYhclaMQiu2dI9wFLHErHjiyTBfIYssn8zmhMUn0mGoFEhwWRyE3FWe1iO_P-zRpU"

# 📂 مجلد Drive الهدف
FOLDER_ID = "1lLKbFPovufWeEkwpCgI3cM-Je-Uee9el"

# 🔧 الصلاحيات المطلوبة
SCOPES = ["https://www.googleapis.com/auth/drive"]

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
    return build("drive", "v3", credentials=creds)

def delete_all_in_folder(service, folder_id):
    print(f"🚮 جاري حذف كل الملفات من المجلد: {folder_id}")
    page_token = None
    total_deleted = 0

    while True:
        # جلب الملفات داخل المجلد
        response = service.files().list(
            q=f"'{folder_id}' in parents",
            fields="nextPageToken, files(id, name)",
            pageToken=page_token
        ).execute()

        files = response.get("files", [])
        if not files:
            if total_deleted == 0:
                print("📭 المجلد فارغ بالفعل.")
            else:
                print(f"✅ تم حذف {total_deleted} ملف بنجاح.")
            break

        for file in files:
            try:
                service.files().delete(fileId=file["id"]).execute()
                print(f"🗑️ تم حذف: {file['name']}")
                total_deleted += 1
            except Exception as e:
                print(f"❌ فشل حذف {file['name']}: {e}")

        page_token = response.get("nextPageToken", None)
        if not page_token:
            print(f"✅ تمت العملية بنجاح. مجموع الملفات المحذوفة: {total_deleted}")
            break

def main():
    service = get_drive_service()
    delete_all_in_folder(service, FOLDER_ID)

if __name__ == "__main__":
    main()
