import os
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from datetime import datetime, timedelta

# إعداد تصاريح Google Drive API من ملف الخدمة (service account)
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

# إعداد التصريحات من Google API لـ YouTube باستخدام حساب الخدمة
# إعداد التصريحات من Google API لـ YouTube باستخدام حساب الخدمة
def get_youtube_service():
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
        scopes=["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.force-ssl"]
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
