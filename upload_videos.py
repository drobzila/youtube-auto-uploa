import os
import google.auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import json
import time
from datetime import datetime, timedelta
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.service_account import Credentials as ServiceAccountCredentials

# بيانات الاعتماد مباشرة في السكربت

google_drive_credentials_json = '''
{
  "type": "service_account",
  "project_id": "able-rarity-466017-d7",
  "private_key_id": "cc6532c6ff3f85a79edbba4395bda950050bb423",
  "private_key": "-----BEGIN PRIVATE KEY-----\\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCw8QrI4kx0Zvap\\npUcGY/tSxR/qHhxw4jv18vEMGqUgdhBpd1cPNu3JVS7Kf1bz8VE68zju0Z22bJ9r\\nT63dBf+Uc+K5Q0Blj3k1QjhLJh2CuI9RWLfyWGFsODmu44igpMarFJUEzfuhuRAz\\nBY0ZRXIvfcKCwhRu8RYUcKfPF+HbJ9sVy+1wedm+9tANuLb2DtyxsruwAz+KcpBp\\nc0WPV+xw2x4kRfE+gy0fbqsCsrRwljyHFu+O4GtlKes2K7mZKRHsfChM3iwQFSpy\\nl9swujQ/9tHxHBDfBc/FnvT6DqM9dR5hdE+/OgLRlNVfbPgoP1Ck95LJ0DZXvCsr\\nGaC6Ad85AgMBAAECggEACEZBZ5sDkcb13oGS5Hbc/CYpQ6jEUjgWLz587MC7O50h\\nz9jLmrPKI2nnHgOd9JrynkPdA/gL/MmwG9PWUNl0tgPEVL8THhy7QZUW7la6NxB7\\n7UUtlvjwl1+6vNW5oC+Mddgozth2Hb46hnRKQKYJfLSQGc7LJ1QBYRPSmSHoBzhO\\nKsiS1nP/j2WGzNiO4T7XOw3bzBgKF2F0ZTQjWvfF0rch09RCtCpp7Af+kWow+LNC\\nndqHvvYyOcUFTyeblTDOM+MZxuEx4D9PlS0UwYWzTkK38r/diR30s88rknAltlDK\\nnDXwn8uze8K6iIsT9M/VnDxvJv2QIVB3TlQ/H0DIvQKBgQDrBi49sd1wFBFUer3K\\nniCZKtc8M8yY+B2nSPEbOIFBm1TC5KmIHwI2+0zjkTJMLmnl967MdG7b0aTRyk03\\nGWVdHIsor6PiHg2ZRLoDfu2E+FvDP3yCNFtMzRdHsEEacsRpPPwQg44WSu9pj0KW\\nCxdyfhZHtXrGgJ8YFPeZbbOn7QKBgQDAu8s+A/8qYZH/ms1WpwQBK60sAB8pw0wt\\n9rg0ZVIEe/EwNm+oDG2YkhtWxLJ47o+LvRtH4NVShLGNQ3KG3AiApvxzCLZ/iPlx\\nmxGocw0J1HpRH8YVMabp+8cGF8/8ZqmHuPuSGLUxgSLmr0QhrekfPLLcEt/2SvZZ\\nH3vj9vdS/QKBgCe85sqlrURLEFcRXc/Jhsd/F99k/r4KjbEAQ0wP9MLsCZveX8/V\\nNmGngeukXDXHTz6D73lAYpImU1DpfL7JO3tP3TOm5vXPkQsONMlsh6qI97L+pAW7\\n5ogI0VvcsFVRfGYy2ofMRpT8XJijkWWfQHqqWQgM5lJz4vKGcQrvIoZNAoGBAJpk\\n1ge0A/DbgK2WQPAtkxOs/WjGIDDAdoJLpnyyveVBtJC+yuuAKTuTr7ruj1o5IVz7\\n/KK0Ba+5BNL5OQG3ukf1fT5ZuHiqLclIQ/kBUWySffoGzhOkVuYR//ltkfvL8fr7\\nwOvkRyKFJIRP2vBv9NRFN7L8m9UdcAMtKX4RFUexAoGBAJazDDH+xBQa0SRgeTnJ\\nJLFx3lPnwekJSZPVEtV9bvmYpcbXoWKZQJ4wKInjGKx87LScs2Db/7vDikWib4Sd\\nTlbq7iIow9wRyb+pwynoahj+N9iaW/GapXc7lVU1EcV9fcGYI/E4X2yY1wLSCTX2\\n4PRjke73ciLDrsb2IhJeDwAU\\n-----END PRIVATE KEY-----\\n",
  "client_email": "googeldrive-uploader-service-a@able-rarity-466017-d7.iam.gserviceaccount.com",
  "client_id": "109947952583981958040",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/googeldrive-uploader-service-a%40able-rarity-466017-d7.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
'''

client_secrets_json = '''
{
  "installed": {
    "client_id": "406439852525-q9tmb4ucd1rgckts41mnlkjga2ht4plu.apps.googleusercontent.com",
    "project_id": "ambient-depth-466117-a8",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "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",
    "redirect_uris": ["http://localhost"]
  }
}
'''

# تحويل JSON إلى Python objects
google_drive_credentials_info = json.loads(google_drive_credentials_json)
client_secrets_info = json.loads(client_secrets_json)

# توثيق الوصول إلى Google Drive باستخدام Service Account
def authenticate_google_drive(credentials_info):
    credentials = ServiceAccountCredentials.from_service_account_info(
        credentials_info,
        scopes=['https://www.googleapis.com/auth/drive']
    )
    drive_service = build('drive', 'v3', credentials=credentials)
    return drive_service

# توثيق الوصول إلى YouTube باستخدام OAuth 2.0
def authenticate_youtube_oauth(credentials_info):
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    creds = None

    # إذا كان هناك ملف credentials المحفوظ سابقًا
    if os.path.exists('token_youtube.pickle'):
        with open('token_youtube.pickle', 'rb') as token:
            creds = pickle.load(token)

    # إذا لم يكن هناك توثيق، قم بعمل توثيق جديد
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(credentials_info, SCOPES)
            creds = flow.run_local_server(port=0)

        # حفظ بيانات التوثيق لتستخدم لاحقًا
        with open('token_youtube.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('youtube', 'v3', credentials=creds)

# التوثيق ورفع الفيديوهات
def upload_video_to_youtube(file_path, title, description, tags, youtube_service):
    # تحميل الفيديو إلى YouTube
    media = MediaFileUpload(file_path, mimetype='video/*')
    request = youtube_service.videos().insert(
        part="snippet,status",
        body=dict(
            snippet=dict(
                title=title,
                description=description,
                tags=tags
            ),
            status=dict(
                privacyStatus="public"
            )
        ),
        media_body=media
    )
    response = request.execute()
    print(f"تم رفع الفيديو: {response['id']}")
    return response

# الاستخدام
google_drive_service = authenticate_google_drive(google_drive_credentials_info)
youtube_service = authenticate_youtube_oauth(client_secrets_info)

# استبدل هذه القيم بمعلومات الفيديو الذي ترغب في رفعه
video_file_path = "path_to_your_video.mp4"
video_title = "عنوان الفيديو"
video_description = "وصف الفيديو"
video_tags = ["tag1", "tag2", "tag3"]

# رفع الفيديو إلى يوتيوب
upload_video_to_youtube(video_file_path, video_title, video_description, video_tags, youtube_service)
