import os
import io
import json
import random
import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google.auth.transport.requests import Request

# -------------------------
# ⚠️ تذكير أمني:
# لا تضع مفاتيح أو ملفات JSON داخل الكود. استخدم متغيرات بيئية أو GitHub Secrets.
# يجب تعيين:
# - SERVICE_ACCOUNT_JSON (محتوى JSON كـ string) أو GOOGLE_APPLICATION_CREDENTIALS (مسار ملف JSON)
# - YOUTUBE_REFRESH_TOKEN, YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET
# - DRIVE_FOLDER_ID (اختياري إذا تريد تغيير المجلد)
# -------------------------

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

# -------------------------
# 🎯 إعداد خدمات Google Drive و YouTube
# 🧩 إنشاء خدمة Google Drive
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

# -------------------------
def get_drive_service():
    sa_json = os.getenv("SERVICE_ACCOUNT_JSON")
    if sa_json:
        info = json.loads(sa_json)
        creds = service_account.Credentials.from_service_account_info(info, scopes=["https://www.googleapis.com/auth/drive"])
    else:
        creds = service_account.Credentials.from_service_account_file(
            os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
            scopes=["https://www.googleapis.com/auth/drive"]
        )
    return build('drive', 'v3', credentials=creds)

def get_youtube_service():
    refresh_token = os.getenv('YOUTUBE_REFRESH_TOKEN')
    client_id = os.getenv('YOUTUBE_CLIENT_ID')
    client_secret = os.getenv('YOUTUBE_CLIENT_SECRET')
    if not (refresh_token and client_id and client_secret):
        raise RuntimeError("يجب تعيين YOUTUBE_REFRESH_TOKEN و YOUTUBE_CLIENT_ID و YOUTUBE_CLIENT_SECRET في المتغيرات البيئية.")
    creds = Credentials(
        None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=["https://www.googleapis.com/auth/youtube.upload"]
    )
    creds.refresh(Request())
    return build('youtube', 'v3', credentials=creds)

# -------------------------
# ⬇️ تنزيل ورفع الفيديو
# -------------------------
def download_video_from_drive(file_id, file_name, drive_service):
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.FileIO(file_name, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    return file_name

def upload_video_to_youtube(file_path, title, scheduled_datetime, youtube_service, original_title):
    body = {
        "snippet": {"title": title},
        "status": {
            "privacyStatus": "private",
            "publishAt": scheduled_datetime.isoformat(),
            "selfDeclaredMadeForKids": False
        }
    }
    media = MediaFileUpload(file_path, mimetype="video/*", resumable=True)
    request = youtube_service.videos().insert(part="snippet,status", body=body, media_body=media)
    response = request.execute()

    print(f"✅ Uploaded: '{title}' scheduled at {scheduled_datetime.isoformat()} | ID: {response.get('id')}")
    with open("log.txt", "a", encoding="utf-8") as log:
        log.write(f"{original_title} - {response.get('id')} - {scheduled_datetime.isoformat()} - title:{title}\n")

# -------------------------
# 🧠 تجنّب التكرار في العناوين
# -------------------------
def is_already_uploaded(title):
    if not os.path.exists("log.txt"):
        return False
    with open("log.txt", "r", encoding="utf-8") as f:
        return title in f.read()

def pick_random_title(used_titles=set()):
    """
    يختار عنوانًا عشوائيًا من video_titles:
    - ليس مستخدماً مسبقًا في هذا التشغيل (used_titles)
    - ولم يُستخدَم سابقًا حسب log.txt
    """
    available = [t for t in video_titles if t not in used_titles and not is_already_uploaded(t)]
    if not available:
        # إن نفدت الخيارات، نسمح بالاختيار من كل العناوين مع محاولة الانتباه للتكرار
        available = [t for t in video_titles if t not in used_titles]
    if not available:
        # كملاذ أخير، ارجع أي عنوان عشوائي
        return random.choice(video_titles)
    return random.choice(available)

# -------------------------
# 🚀 الكود الرئيسي: جدولة 5 فيديوهات بالأوقات المطلوبة (UTC+1)
# -------------------------
def main():
    drive_service = get_drive_service()
    youtube_service = get_youtube_service()

    folder_id = os.getenv('DRIVE_FOLDER_ID', '1_iPtcfFs3TpusMr9THwTc31SWtLtwccZ')  # اضبط معرف المجلد إن لزم
    files_resp = drive_service.files().list(q=f"'{folder_id}' in parents and mimeType contains 'video/'",
                                            fields="files(id, name)", pageSize=50).execute()
    files = files_resp.get('files', [])

    if not files:
        print("❗ لا توجد فيديوهات في المجلد.")
        return

    # نأخذ أول 5 ملفات (أو أقل إذا لم تتوفر)
    target_files = files[:5]

    # أوقات الرفع المطلوبة بتوقيت الجزائر UTC+1
    target_hours = [7, 10, 12, 16, 21]  # بالترتيب
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=1)))

    scheduled_datetimes = []
    today = now.date()
    for hour in target_hours:
        sched = datetime.datetime.combine(today, datetime.time(hour, 0), tzinfo=datetime.timezone(datetime.timedelta(hours=1)))
        # إن تجاوز الوقت الآن نضعه لليوم التالي
        if sched <= now:
            sched = sched + datetime.timedelta(days=1)
        scheduled_datetimes.append(sched)

    used_titles = set()  # عناوين مستعملة في هذا التشغيل لتجنّب التكرار داخل التشغيل
    uploaded = 0

    for (file, sched_time) in zip(target_files, scheduled_datetimes):
        original_title = file['name']
        # اختيار عنوان عشوائي وغير مكرر
        new_title = pick_random_title(used_titles)
        used_titles.add(new_title)

        print(f"⬇️ Preparing to download '{original_title}' (ID: {file['id']}) for schedule {sched_time.isoformat()}")
        path = download_video_from_drive(file['id'], original_title, drive_service)
        upload_video_to_youtube(path, new_title, sched_time, youtube_service, original_title)

        try:
            os.remove(path)
        except Exception as e:
            print(f"⚠️ لم أستطع حذف الملف المحلي {path}: {e}")

        uploaded += 1

    print(f"✅ انتهى: عدد الفيديوهات المجدولة/المحمّلة = {uploaded}")

if __name__ == "__main__":
    main()
    media = MediaFileUpload(file_path, mimetype="video/*", resumable=True)
    request = youtube_service.videos().insert(part="snippet,status", body=body, media_body=media)
    response = request.execute()

    print(f"✅ Uploaded: {title} at {scheduled_datetime.time()} | ID: {response['id']}")
    with open("log.txt", "a", encoding="utf-8") as log:
        log.write(f"{original_title} - {response['id']} - {scheduled_datetime}\n")

# 🧠 التحقق من وجود العنوان مسبقاً
def is_already_uploaded(title):
    if not os.path.exists("log.txt"):
        return False
    with open("log.txt", "r", encoding="utf-8") as f:
        return title in f.read()

# 🧩 العنوان الفريد
def make_unique_title(title):
    if is_already_uploaded(title):
        new_title = random.choice(video_titles)
        print(f"⚠️ '{title}' مكرر — تم استبداله بـ '{new_title}'")
        return new_title
    return title

# 🚀 الكود الرئيسي
def main():
    drive_service = get_drive_service()
    youtube_service = get_youtube_service()

    folder_id = '1_iPtcfFs3TpusMr9THwTc31SWtLtwccZ'
    files = drive_service.files().list(q=f"'{folder_id}' in parents", fields="files(id, name)").execute().get('files', [])

    if not files:
        print("❗ لا توجد فيديوهات في المجلد.")
        return

    today = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=1))).date()
    times = [datetime.time(12, 0), datetime.time(16, 0), datetime.time(21, 0)]
    schedule = [
        datetime.datetime.combine(today, t, tzinfo=datetime.timezone(datetime.timedelta(hours=1)))
        for t in times
    ]

    uploaded = 0
    for file, sched_time in zip(files, schedule):
        if sched_time <= datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=1))):
            print(f"⏩ تجاوز {file['name']} لأن وقته {sched_time.time()} قد مر.")
            continue

        original_title = file['name']
        new_title = make_unique_title(original_title)

        path = download_video_from_drive(file['id'], original_title, drive_service)
        upload_video_to_youtube(path, new_title, sched_time, youtube_service, original_title)
        os.remove(path)  # 🧹 حذف الفيديو بعد الرفع
        uploaded += 1

        if uploaded >= 3:
            break

    if uploaded == 0:
        print("✅ لا توجد فيديوهات مناسبة للرفع اليوم.")

if __name__ == "__main__":
    main()
