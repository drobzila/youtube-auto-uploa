import os
import io
import random
import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from google.auth.transport.requests import Request

# 📋 قائمة العناوين الجاهزة
video_titles = [
    "استمتع بسكينة القرآن", "عِش راحة القرآن", "لحظة مع كلام الله", "جمال التلاوة", "نور قلبك بالقرآن",
    "همسات قرآنية", "ترتيل يشرح الصدر", "أنفاس قرآنية", "رحلة مع القرآن", "معاني تطمئن القلب",
    "روعة الصوت القرآني", "طمأنينة من السماء", "قرآن يهز المشاعر", "موسيقى السماء", "صوت الملائكة",
    "صفاء النفس بالقرآن", "ترانيم الرحمة", "آيات تلين القلوب", "نور بين السطور", "سكون القلب",
    "قرآن الشفاء", "خُشوع لا يُوصف", "صوت يحيي الأرواح", "صدى الجنة", "بصوت من الجنة",
    "عيش القرآن بجوارحك", "هدوء القرآن", "نفحات قرآنية", "إيمان متجدد", "تلاوة تذيب القلوب",
    "صوت يهز الوجدان", "لحظة روحانية", "القرآن كما لم تسمعه من قبل", "سافر مع القرآن", "تأمل آية",
    "حديث الله إليك", "بوح السماء", "قرآن ينير الدرب", "صوت يرقى بالروح", "لحن الرحمة",
    "ركن الهدوء", "أنفاس السكينة", "نبض التلاوة", "فيض القرآن", "القرآن حياة", "ذِكر طيب",
    "أصوات من الجنة", "نور التلاوة", "رحمة القرآن", "مرفأ الطمأنينة", "سُطور نورانية",
    "طيف من الجنة", "السكينة في التلاوة", "بوح من السماء", "صفحة من نور", "عبق القرآن",
    "صوت الإيمان", "تلاوة تهدئ القلب", "آية تغير الحياة", "أمان الروح", "صوت يلامس القلب",
    "من أعماق الإيمان", "كلام الله يصل الأعماق", "هُدى ونور", "ارتقاء بالقرآن", "صوت يطهر القلب",
    "لحظة مع الإيمان", "في حضرة القرآن", "أنغام السماء", "آيات تلامس الأرواح", "خشوع لا يُضاهى",
    "جمال من الجنة", "صوت ينقلك لعالم آخر", "نورك في القرآن", "شوق للآيات", "بوح الإيمان",
    "نقاء التلاوة", "عذوبة القرآن", "صوت يحملك للسكينة", "مرفأ الإيمان", "القرآن طمأنينة",
    "هُدى الرحمن", "بوح الروح", "دقائق مع الله", "لحظات إيمانية", "ترتيل من القلب", "نور الروح",
    "ترانيم إيمانية", "صوت هادئ ونقي", "عبادة بالصوت", "أنفاس الإيمان", "همس التلاوة",
    "لحظة نقاء", "فيض نوراني", "آيات تتغلغل في القلب", "ترتيل مطمئن", "صوت مريح للنفس",
    "رحلة سماوية", "بوح الآيات", "دعاء يتلى", "القرآن رفيقك", "صوت يتسلل إلى روحك"
]

# 🧭 مجلد الفيديوهات في Google Drive

FOLDER_ID = "1lLKbFPovufWeEkwpCgI3cM-Je-Uee9el"

# 🧩 إنشاء خدمة Google Drive

def get_drive_service():
    credentials = ServiceAccountCredentials.from_service_account_info(
        {
  "type": "service_account",
  "project_id": "youtubeuploader-465800",
  "private_key_id": "4c7271f51c474e7c3ec760ee19975fd8854d0d83",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDRKvmezTjo8x0G\n+GUopfvN9a1IYa9Eu0mw67JbucUd5lNZ0IasIlm6B2DlYPys+I4GjysdwgcMhwtu\niPuZaRQkoKcKHxavo7t3TZnrQA3wlth+AJ6jnjp6gqZa4w9LdrqvOVHOyV8nekyc\nAjPLEgH2VM6mqg/sWuuGaiuXZoHAx2i9yVD/9NkYHcY46iNS7iuyFyN4w35fmZdh\nUXkAM0a1S/MwHKa6pM2WG31Jtt/+qjN+/Llmp/rgRcu8EsJVK3AzebiltvGGn17b\ngqvp0w75wU2bJzyIxV3WIFvNXmubs6/dBPeXC1nnGzShzq4Oj/Rk83lffCu9kT84\nj9yL+onzAgMBAAECggEAOoiwOkRr/KSsJts0U9+/S6/Iwkyz46QVxzDuRMUD6I4g\nHS5BwcILIggWkZpGm5EjDarbAgTePB8+j7w9zHyfanCazjZM/vHu8EADJtZSEFXm\nV7yMqHULIGWXcC/Cg/fB3m9H+XpY6o9LCQ2EuPtdGTY6bmGA+z+mUYM8l63T+cJS\nOQBrLFITv0IxcTrSKqkJHQ6YNc7Xy1tZ66alqB7+7d2q+97WBBr+4aFJjia8uZ50\nLh2f03T7JauXtO9bKEwofYESHL1NQSkylHHpt96pkpFlVpQKzUlhSh64KQfrlexr\no6pbfMvEJchzyQw/IWLiAMi6f1mvN7rpj52PU2ugYQKBgQD3swxWb5Pm88yxwAI/\nZ9IupMryyus6vjdlAQl4nqPbs5MXnSjl+v4DDsKX5t3Su6mg7NJylgffuTu+izn8\nqFIthRQKWfkbwhA3p0ZjEWmdtR4MDITmkQJM+fOmy58toSz1Jcdxc1tOATcIsr57\nHE6m0aKNBWFbEQe3A8DrYjmElwKBgQDYLV/YRXzOY6lYGHn2Czmjvmhssf1fIEA7\nUtE5SxsSm+2Nqe4y8cbMXMyYkOgy1UymRcI69oaNr/Zg7095d154UJLpdHPwQTPs\ncYjb40tT4dNUpyBHUhlnzQsebOROtAHvCAEt0kqxtD8MQUA2xq0goi+LXeYgqimX\nPwnOXVwFBQKBgQDRFnHOsMb/iEL8tGDxVtkkCHVMN6AS6ShneVWeXQNiXJZIs6An\nahRrTlVS1k3fKgxJTD9k/GJPJtRYxru/G/KqfBBroIFYPhtkby5KSBOITa+8agDx\ng+yWP9O9s1p9sPT7RtWxXbfwA7SKAiAqWb3GsWTud2Ez9w81HNUHnNWCpwKBgB1g\nfSfcuYsqi/bGzLwc5mZUF8i9n1rv/QqSxI/unu02d1/K+e2+YW+gJMWO258c0V+/\nFxgALGTQxsCBhOFS0Wm0OWK0SpUZpz64ZwrKpo/tnlRgqchHZeBvQtWNorD3UVP0\nWISrkS74+aBmtZ07/obyw1dDGWTS+vfsvx5mHX0pAoGAdQQdV6ivM8cGKcIj5CK9\nLjpGIfnBw+dYMwRLUdbjNruYOC8WyHjOiVvM1l5yz77pKngIk9O86pXe6WqfNmRx\ncxFLr9th/69lJ4dDtlzQCeYvY1fr3zpPYtWiT4VTDpT+4uBQUguy/G07MkHTPLgh\nKG1aY1eBb9bwbGLkc04Db6s=\n-----END PRIVATE KEY-----\n",
  "client_email": "youtubevideos@youtubeuploader-465800.iam.gserviceaccount.com",
  "client_id": "111374510118265897026",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/youtubevideos%40youtubeuploader-465800.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
},
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    return build('drive', 'v3', credentials=credentials)

# 🧩 إنشاء خدمة YouTube
def get_youtube_service():
    creds = Credentials(
        None,
        refresh_token=os.getenv('YOUTUBE_REFRESH_TOKEN'),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv('YOUTUBE_CLIENT_ID'),
        client_secret=os.getenv('YOUTUBE_CLIENT_SECRET'),
        scopes=["https://www.googleapis.com/auth/youtube.upload"]
    )
    creds.refresh(Request())
    return build('youtube', 'v3', credentials=creds)

# ⬇️ تحميل الفيديو من Google Drive
def download_video_from_drive(file_id, file_name, drive_service):
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.FileIO(file_name, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    print(f"⬇️ تم تحميل {file_name}")
    return file_name

# 🎥 رفع الفيديو إلى YouTube مع الجدولة
def upload_video_to_youtube(file_path, title, scheduled_datetime, youtube_service, original_title):
    body = {
        "snippet": {
            "title": title,
            "description": "تلاوة قصيرة من القرآن الكريم 🌿 #قرآن #Quran #تلاوة",
            "tags": ["قرآن", "Quran", "تلاوة", "راحة", "إيمان"]
        },
        "status": {
            "privacyStatus": "private",
            "publishAt": scheduled_datetime.isoformat(),
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(file_path, mimetype="video/*", resumable=True)
    request = youtube_service.videos().insert(part="snippet,status", body=body, media_body=media)
    response = request.execute()

    print(f"✅ Uploaded: {title} | Publish at {scheduled_datetime.time()} | ID: {response['id']}")
    with open("log.txt", "a", encoding="utf-8") as log:
        log.write(f"{original_title} - {response['id']} - {scheduled_datetime}\n")

# 🧠 التحقق من رفع العنوان مسبقًا
def is_already_uploaded(title):
    if not os.path.exists("log.txt"):
        return False
    with open("log.txt", "r", encoding="utf-8") as f:
        return title in f.read()

# 🧩 إنشاء عنوان فريد (يتجنب التكرار)
def make_unique_title():
    while True:
        new_title = random.choice(video_titles)
        if not is_already_uploaded(new_title):
            return new_title

# 🚀 الكود الرئيسي
def main():
    tz = datetime.timezone(datetime.timedelta(hours=1))  # الجزائر +1
    now = datetime.datetime.now(tz)

    # أوقات النشر اليوم (7، 10، 12، 16، 21)
    today = now.date()
    schedule_times = [7, 10, 12, 16, 21]
    schedule = [
        datetime.datetime.combine(today, datetime.time(h, 0), tzinfo=tz)
        for h in schedule_times
    ]

    drive_service = get_drive_service()
    youtube_service = get_youtube_service()

    files = drive_service.files().list(
        q=f"'{FOLDER_ID}' in parents and mimeType contains 'video/'",
        fields="files(id, name)"
    ).execute().get("files", [])

    if not files:
        print("⚠️ لا توجد فيديوهات في المجلد.")
        return

    random.shuffle(files)  # عشوائية في الاختيار
    selected_files = files[:5]

    for file, sched_time in zip(selected_files, schedule):
        original_title = file["name"]
        new_title = make_unique_title()

        # تحميل الفيديو
        path = download_video_from_drive(file["id"], original_title, drive_service)

        # رفع الفيديو المجدول
        upload_video_to_youtube(path, new_title, sched_time, youtube_service, original_title)

        # حذف الفيديو المؤقت
        os.remove(path)
        print(f"🧹 حذف {original_title} بعد الرفع")

    print("✅ تم جدولة ورفع 5 فيديوهات اليوم بنجاح.")

if __name__ == "__main__":
    main()
