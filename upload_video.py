import os
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from google.oauth2.credentials import Credentials
from datetime import datetime, timedelta

# إعداد تصاريح Google API من ملف الخدمة (service account)
def get_drive_service():
    credentials = ServiceAccountCredentials.from_service_account_info(
        {
            "type": "service_account",
            "project_id": "youtube-auto-publisher-465723",
            "private_key_id": "7cd44640375f00a88b3fa6a58186750db9eda202",
            "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEuwIBADANBgkqhkiG9w0BAQEFAASCBKUwggShAgEAAoIBAQDRGbTrEr+igWOp\nTUagrAXQQ6kAIlsvGc6DuUBOYJb+L1i2B7SLuZexXpwlBal9VG906sFkA1D48Kb2\n3+hPuKuhnuWyYnyLJaCPazE7kLNEl8tYtbnlFhXNFNxIqFNSn2jQbRj3rVCsuIiM\nINxHWO8MOQQWyjYOD0Nr3Nan58okKEw5h0fkz30115/yu7MQbjHg+9aXMpy926YW\nUzH5anhZ2cyESmfVe8r88goDqBF155WLMzmAR+SKOh3mPWR1uH54vaP/UcqJ98ys\ncpq785zPEPe154OAVDG2ZFbdSg1N5SngRu1nVw4yCmBEmMhnTzfSrcHxQEwx8adM\n0P9fLQ35AgMBAAECgf83P4bG94khgaXGvFr3byPm5HK4baFGEKrxCV1zMtNjWD14\n1o4GdF8fG2iKbaHw57NTelsoEvloLt6fn7E+kmGmVgMAIERtNSEFRkd+MOYxmhPL\nhVku281m2AYRs4iRqAhJsWkuZQII/gzLqnylSr0ty4pheyXdd4phC6hhY3DahR2m\noiHp71jNNgGh8Cfoxd5pkmow2UK0/F/Hh+05IAxDgmNJIDPXHB9rw62tw9vtMXJM\nLn20pm+E71ZxOChmiEMdZdjngIU2qmqJ+sVKo2beZyk7tION5GOKMHi0fOCxJH3/\nUYOnQgwALmjGfvJ5MbO4e8Y/tI4t/eQpFKwy6E0CgYEA8svzsQlF4+NfwgDRFeIg\nPFzAfjyBdK8tuCrnZwL3Y34w7yt+ehxJuSWjn0VwvUTye0U4Q+UGaBwLGLRU27AS\n1n1Rl1b4UAFqClQQUAabFS1i3BwF/+u3nAwcebNHzVB1VZSGtT4a5IoKGhPW36Da\nshOtvOjLf3nrHVV1EPQcdh0CgYEA3HiolqCnbFFoBu4eRF73Y8rrkw4Ep8CKAwn4\nxE6FzgpSU7TQ9l4O5EGrqQtcxkM8ZDIow0ipmRp22f+LmkLfNE1J0iinNlmbh5iV\nwvJ8fgFqJU3m8aUjZbyZQsUcjNO2HM+f3jE4EUfmo1rMskV7TrERlep6qshLFUk7\nSsGAAI0CgYBO+UIB0rdWAc5S5zsbOBsuJylBpmKhVp2zatkr644WYaR/FxGjnHHq\ndDC9jLO4DKYmrIQ5qVQlJwIA/h8f+iyWcdrJNDO+qkcYpvFLZmqpP8MJP2BANybY\n7iOQ/lybjtErjg0nBNVwgun4Q32/7a1VAQuhB8OxajGsr/BNHGnpjQKBgEQ66yHC\nkk3JW8JZSvCp2zH9CK639eTch1mtalmGW46KTzQsj0bPkRg+4pssMwgAot33T/ov\nsJz7PbD1jwSskVskWCY8ApOlY6axKBfu52wvj+P/metKygugNGYfjlhe5MtBzh37\naXifodcIMLUzH5gY4HJe4Jud5O6vfTQDclO5AoGBAL9rWnWxc30FOqpP0rxnE4DH\n/7G63qOixioWTCu3OjmXRhsTbjS4Q8GRFmSaB6A6eIsjwPHGUitacW1Fstfwm7p7\nYjTp+5lYIqQvyextaqFrLZ+GNwB2ei46CIqu6vBI3H7d4sI/ZNFPgge9LwB5i7x3\nrB4ynEOhaOt/fpyjdgpb\n-----END PRIVATE KEY-----\n",
            "client_email": "youtube@youtube-auto-publisher-465723.iam.gserviceaccount.com",
            "client_id": "112957862105787070183",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/youtube%40youtube-auto-publisher-465723.iam.gserviceaccount.com",
            "universe_domain": "googleapis.com"
        },
        scopes=["https://www.googleapis.com/auth/drive.readonly", "https://www.googleapis.com/auth/youtube.upload"]
    )
    drive_service = build('drive', 'v3', credentials=credentials)
    return drive_service

# تحميل الفيديو من Google Drive
def download_video_from_drive(file_id, file_name, drive_service):
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.FileIO(file_name, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print(f"Download {int(status.progress() * 100)}%.")
    return file_name

# إعداد التصريحات من Google API لـ YouTube
def get_youtube_service():
    credentials = Credentials.from_authorized_user_info(
        {
            'client_id': os.getenv('YOUTUBE_CLIENT_ID'),
            'client_secret': os.getenv('YOUTUBE_CLIENT_SECRET'),
            'refresh_token': os.getenv('YOUTUBE_REFRESH_TOKEN'),
        },
        scopes=["https://www.googleapis.com/auth/youtube.upload"]
    )
    youtube_service = build('youtube', 'v3', credentials=credentials)
    return youtube_service

# البحث عن الفيديو في قناة يوتيوب باستخدام العنوان
def is_video_in_youtube(youtube_service, title):
    request = youtube_service.search().list(
        part="snippet",
        q=title,
        type="video",
        maxResults=1,
        order="date"
    )
    response = request.execute()

    if "items" in response and len(response["items"]) > 0:
        return True  # تم العثور على فيديو بنفس العنوان
    return False  # لا يوجد فيديو بنفس العنوان

# رفع الفيديو إلى YouTube مع جدولة
def upload_video_to_youtube(file_path, title, description, scheduled_time, youtube_service):
    media = MediaFileUpload(file_path, mimetype="video/*", resumable=True)

    request = youtube_service.videos().insert(
        part="snippet,status",
        body=dict(
            snippet=dict(
                title=title,
                description=description,
            ),
            status=dict(
                privacyStatus="public",  # يمكن تغييرها إلى "private" أو "unlisted" حسب الحاجة
                publishAt=scheduled_time,  # تحديد وقت النشر
            ),
        ),
        media_body=media
    )

    response = request.execute()
    print(f"Video uploaded successfully! Video ID: {response['id']}")

# تنفيذ العملية
def main():
    folder_id = '1_iPtcfFs3TpusMr9THwTc31SWtLtwccZ'  # معرف المجلد في Google Drive

    # إعداد Google Drive API
    drive_service = get_drive_service()

    # استرداد الملفات من المجلد
    results = drive_service.files().list(q=f"'{folder_id}' in parents", fields="files(id, name)").execute()
    files = results.get('files', [])

    if not files:
        print("No files found in this folder.")
        return

    # اختيار 3 فيديوهات من المجلد
    videos_to_upload = files[:3]

    # إعداد YouTube API
    youtube_service = get_youtube_service()

    # جدولة الفيديوهات على YouTube
    for i, video in enumerate(videos_to_upload):
        video_id = video['id']
        video_name = video['name']

        print(f"Found video: {video_name}, downloading...")

        # التحقق إذا كان الفيديو موجودًا في يوتيوب بناءً على العنوان
        if is_video_in_youtube(youtube_service, video_name):
            print(f"Video '{video_name}' is already uploaded on YouTube. Skipping.")
            continue

        # تنزيل الفيديو من Google Drive
        downloaded_video_path = download_video_from_drive(video_id, video_name, drive_service)

        # تحديد وقت الجدولة
        scheduled_time = (datetime.utcnow() + timedelta(hours=12 * (i + 1))).isoformat() + 'Z'

        # رفع الفيديو إلى YouTube مع الجدولة
        upload_video_to_youtube(downloaded_video_path, video_name, 'This video was uploaded from Google Drive using script.', scheduled_time, youtube_service)

if __name__ == '__main__':
    main()
