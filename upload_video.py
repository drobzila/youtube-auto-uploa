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
  "private_key_id": "7588bd1bebc2b6c50072c1c0b08b0fba897293b3",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCoNqkMb5wtjVqm\nkNIZBdFSDFPqqhjBkNt2pvNSjGZlovq0/nJ28C3T9BJ+4/snIxDM8HA8j/A2GpjP\n5FcCIxlMoRaHxgLNRbuHVcXcHrEfXLZeawpaPamkiT+DnSiEnf8RkvI9phw42x4C\noZQK1nLNtO8U4oBLDhbIcFl6/vP8vzszCiujMBVnF6DZsDt7ia7bTgf09xWeM4g8\nu23/4MvJA8J2Voi+Yuz5dGXEbTgreb6ilvd1Ekp4xXHhUmlwvW//gJoPSEd2RNlW\nssZTqrYaBOhyBDoI50oF5p7SFkm+bKK4k/NrlJilNQ40i6+jcreN66Rtaw4DgPkD\npfKVMpBPAgMBAAECggEACk8jSCRU9YO6wQeSIL93ByjDQdf/4WkP0jNEKVR6eBMn\ne0021aw9msZUFdvCCjF/d5fqwQNvTNmPcPpFDNf61nPu7g5IIK174zzx/d4Rq+Li\nOGImBcbOrUtODbJlh88pEToox3d1NlTTf4TIjmt7KLlEh8qj4zWvVsRv73ZNnLk/\n60sNYW+bn4OA0M/AYSbJakr5sXafUIwn8l0sASH4Q/Bwdl1o0sRMWcvvwzBsBiLK\nMjH6z7px66a2YUcrFyiEpeF8ibYjsLLDuIFp3SYkgwBIE7k3W5F2dl9tqBhwvPbZ\nLlZ1UPJ8gmOInUL3ExDTsMa7q1bfwtxJDSccoD7efQKBgQDttGOZNOvrZIxUIeyG\nLI3Dgj/cj90e5YM0IuJKOlfbYk1bXLME5pODpiX8/PU2fPQVlbZZSPElxD4ZMsR3\n4McQFY/PEE46wrP72IE7FiL+SuNK8TFe3no/bYYYIFOLHuKh7qsMxekzCiA0Ac6G\njEsQDAEotpuoXckiICFuMGJyiwKBgQC1KQ24KfDbIKbgeOIxusC8NY+Ogo9JN+DE\n4elOM3uoCJd284g5Oj6PuJDycXnHEmDMla2IO8rdodhi2TkugY0HlKbc9Q3o9Ix4\n9lx6qitqnUUs8XXToGor2Dd6Q53qSge/QU/0OqrjyANriCQ72+rlhF/sHB4S9yOo\nA5lPPwRlzQKBgQCtVuFWhNgRdOY8J+ziPzU1wBKv1Z0q/bU63MFl3bvZuIquuB+3\n0Cj8VLnZDeIHVQFtiBpMa7umjb+3AmVxAdJH8WFIXxydDwTO/6flnZPxGk07hj05\ncEV3YXfquhASIHimG3RSwTP4S0cGhdbEGSRX1Fk4BknmclXM899NCi2QVwKBgHM/\n6992pyjwq9lwbg5PDeBufqad/sQIzXDTe9ZpQEjVNm7RXZ9yo2xRcb0bXeq8kWJ1\n8pER4OyA0yWHpi4k8vCYrFMzfybttRQbPxg2fCp2ZRTDhD8e9YxxIFIjBCqR8D3H\nMjNgw2jnzO0zDkIalWRwg4m1FZjhKwjvSTA2GfkdAoGBALOaDZdPnMePyBZn6VSp\ncLGOJbpj7pvUiwjZA0TaqgXRJYbRWlll6IvPFikWT91QRGv5yjZO3ZibNRPoyJaa\nr1MHJIlGcnrrtMhGi/VrDyBbeiyyzItnBHMywmHtOyhzDaalyGIDEpfkZB1Oj1FI\nbRHoUorMi1Z0CoTyKVJaqwwZ\n-----END PRIVATE KEY-----\n",
  "client_email": "youtubeuploader-465800@appspot.gserviceaccount.com",
  "client_id": "103406387617891827020",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/youtubeuploader-465800%40appspot.gserviceaccount.com",
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
