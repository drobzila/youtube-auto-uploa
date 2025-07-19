import os
import io
import google.auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
import datetime

# إعداد تصاريح Google API من ملف الخدمة (service account)
def get_drive_service():
    credentials = ServiceAccountCredentials.from_service_account_info(
        {
            "type": "service_account",
            "project_id": "able-rarity-466017-d7",
            "private_key_id": "079b667528615f3d89d4e5ee88763e8bf4d0075b",
            "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCufxjiyqBw8YSB\nfCVVulCVMYEuJ3f3Wqv+lwJszEi/qp4KbYS7iLNtiInoZbrGPMrGb5eN5DXjvjkB\ndu1Rw2iWlcuXyCRUWy3TiRG1Zcjmwx/NY/9fXmzWSi7bmN0w7vTKigmhDxsYJGSj\n3PBnrTE932DQWltAQ20XVnJPl/3ZZc6HJOanNAus6AjVVbCOQfQFxb71yFOkygE/\np2drYdR5tZBYHiwP+1Gr2WtczdhDXFgKCrQsiJcrjdzz244F87/OH0hTRNUhLaG6\neX1Eb7Djo+ACGutooSF0Y1PQa2hB7F+r9dPFL6Ge7BGFhhQPbebbO0bTgBUKIwoP\nFSQ6OLpjAgMBAAECggEARZ8/aimnpziuAk3qxZAvm79jR+uGgaJjUpKk7Iz7j8G/\nCfEVjw+la5QZVijUw0i5LUCUCxCdcc9RhmSRnthlMAP3dglseV3h5G9hqetBI9WB\nqFz4JPCTY1K47HRK+L223OMDoYfZ6yGGKB08rFkddw7b3XXXx8W/Tpr2xAwkRCsh\nYdLcRJgQrOD7gOtIkbnvGDUBE0IMNGn23Smwh6bpDkvdEDS7znmuYFaMNnvGtdXJ\nImZPKN+JpsdiOXiypownCkludgXIH0eVgLvGMxYPqKs4xqtV0sp8GPnjqlsv+tI+\n+n0tVei+U4RMSJQEyA4HLOgBKrefzhGzuJWtm60tlQKBgQDs1rtTW9A9xlz6n/sV\ndEk/lflxBqCRf1gtb5aDjGfGDuCQcWuVThA0dsLnKzKCWfuD0gWp/g+PWk2EPdaG\nCLN3T0zuk6r7dZPz3AElL/VpoZn252GKRoW37QOD7ZQvAy8ae8QXuoaQw1rEruQ0\ni86jIpNYejsrXnJKLtDVM5embQKBgQC8nSrVcBIT4bhOn84lPJg6jAC1dB7FdKuk\nEwaZRBxKbe+y7z3YWFr1joXDKMzyGp5HFzuUoh42Dvf6IQNU1xh4Z44yxOFkGUiA\nK4Q8JlohNLmkFZQKHwtrxCl3Do96O4plsweLlEGrOkMuUEwqdSswceo0kSdmXzWD\nFy5msfmiDwKBgFN8hmAmF0wPZqs6RcoUSdXOSjXbfjKLz0uE8GvCzLn2eJayRJhH\nAlNcIexXP+DPU2fuWuzHkDiaPoUFP1/UJV9DZv0atMUbd2IZBZZUR5BK1PlCKxIR\nNgXV2M1irD++QZZ2VnN+3vycwJxggjU7q0W6ZHJl9AGfs24O/rKJE0YpAoGATi7f\n+IVyGOex3HWFoA3UFEDAcnbl4neQRnzUeWewSnHzsDpXanyFh9BCRjl9asX54gIR\nYnUpDMN7qyVQGjTnIdHbMdRGkZWhZe+j6sMDDUyrvwZqzR89Pribb4yLkOFpZuql\nMAiOiAmom2QRjm/vLS+rI4sfx+GjbumHBG61yaUCgYEAyqp6KaH9EMU7wWVI08Xn\nIATOb2GkD/QHO3CCQdfMEulE8vorc8scuUkpPIJ/FHnTEn2aqcZIAQ7TwxUn9SPi\nf6lFEwYlddeLRg4KgtEDdXVywmTdt+/J/aEdWfEpxujmg7Ad9rYOD1YyvCY7SYgL\n+x05lczFEa5jD10b1h0K5LM=\n-----END PRIVATE KEY-----\n",
            "client_email": "googeldrive-uploader-service-a@able-rarity-466017-d7.iam.gserviceaccount.com",
            "client_id": "109947952583981958040",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/googeldrive-uploader-service-a%40able-rarity-466017-d7.iam.gserviceaccount.com",
            "universe_domain": "googleapis.com"
        },
        scopes=["https://www.googleapis.com/auth/drive.readonly", "https://www.googleapis.com/auth/youtube.upload"]
    )
    return build('drive', 'v3', credentials=credentials)

# تحميل الفيديو من Google Drive
def download_video_from_drive(file_id, file_name, drive_service):
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.FileIO(file_name, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        print(f"Download {int(status.progress() * 100)}%.")
    return file_name

# إعداد خدمة YouTube
def get_youtube_service():
    credentials = Credentials.from_authorized_user_info(
        {
            'client_id': os.getenv('YOUTUBE_CLIENT_ID'),
            'client_secret': os.getenv('YOUTUBE_CLIENT_SECRET'),
            'refresh_token': os.getenv('YOUTUBE_REFRESH_TOKEN'),
        },
        scopes=["https://www.googleapis.com/auth/youtube.upload"]
    )
    return build('youtube', 'v3', credentials=credentials)

# تسجيل الفيديو المرفوع في log.txt
def add_uploaded_video_to_log(video_id, video_title):
    with open("log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(f"{video_title} - Video ID: {video_id} - {datetime.datetime.now()}\n")
        log_file.flush()
    print(f"Video '{video_title}' with ID {video_id} added to log.")

# تسجيل video_id في uploaded_videos.txt
def add_uploaded_video_to_file(video_id):
    with open("uploaded_videos.txt", "a", encoding="utf-8") as file:
        file.write(video_id + "\n")
        file.flush()
    print(f"Video ID {video_id} added to uploaded_videos.txt.")

# التحقق من رفع الفيديو سابقًا عبر video_id
def is_video_uploaded(video_id):
    if os.path.exists("uploaded_videos.txt"):
        with open("uploaded_videos.txt", "r", encoding="utf-8") as file:
            return video_id + "\n" in file.readlines()
    return False

# التحقق من وجود العنوان في السجل log.txt
def is_title_in_log(title):
    if os.path.exists("log.txt"):
        with open("log.txt", "r", encoding="utf-8") as log_file:
            for line in log_file:
                if title in line:
                    return True
    return False

# رفع الفيديو إلى YouTube
def upload_video_to_youtube(file_path, title, youtube_service):
    media = MediaFileUpload(file_path, mimetype="video/*", resumable=True)

    request = youtube_service.videos().insert(
        part="snippet,status",
        body={
            "snippet": {"title": title},
            "status": {
                "privacyStatus": "public",
                "madeForKids": False
            }
        },
        media_body=media
    )

    response = request.execute()
    print(f"Video uploaded successfully! Video ID: {response['id']}")
    add_uploaded_video_to_log(response['id'], title)

# العملية الرئيسية
def main():
    folder_id = '1_iPtcfFs3TpusMr9THwTc31SWtLtwccZ'
    drive_service = get_drive_service()
    youtube_service = get_youtube_service()

    results = drive_service.files().list(q=f"'{folder_id}' in parents", fields="files(id, name)").execute()
    files = results.get('files', [])

    if not files:
        print("No files found in this folder.")
        return

    for video in files:
        video_id = video['id']
        video_name = video['name']

        if is_video_uploaded(video_id):
            print(f"Video '{video_name}' already uploaded by ID. Skipping.")
            continue

        if is_title_in_log(video_name):
            print(f"Video '{video_name}' already exists in log by title. Skipping.")
            continue

        print(f"Downloading video: {video_name}")
        downloaded_path = download_video_from_drive(video_id, video_name, drive_service)

        print(f"Uploading to YouTube: {video_name}")
        upload_video_to_youtube(downloaded_path, video_name, youtube_service)

        add_uploaded_video_to_file(video_id)
        break  # ارفع فيديو واحد فقط

if __name__ == '__main__':
    main()
