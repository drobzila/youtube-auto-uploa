import os
import pickle
import google_auth_oauthlib.flow
import googleapiclient.discovery
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRETS_FILE = "client_secret_youtube.json"
TOKEN_PICKLE = "token.pickle"

def get_authenticated_service():
    creds = None
    if os.path.exists(TOKEN_PICKLE):
        with open(TOKEN_PICKLE, "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_console()
        with open(TOKEN_PICKLE, "wb") as token:
            pickle.dump(creds, token)
    return googleapiclient.discovery.build("youtube", "v3", credentials=creds)

def upload_video(youtube, video_path, title):
    request_body = {
        "snippet": {
            "title": title,
            "description": "تم الرفع تلقائيًا من Google Drive",
            "tags": ["قرآن", "تلقائي"],
            "categoryId": "22"
        },
        "status": {
            "privacyStatus": "public"
        }
    }
    media_file = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/*")
    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media_file
    )
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"⬆️ رفع: {int(status.progress() * 100)}%")
    print(f"✅ تم رفع الفيديو: https://youtu.be/{response['id']}")

def main():
    youtube = get_authenticated_service()
    folder = "downloaded_videos"
    for filename in os.listdir(folder):
        filepath = os.path.join(folder, filename)
        upload_video(youtube, filepath, filename)

if __name__ == "__main__":
    main()
