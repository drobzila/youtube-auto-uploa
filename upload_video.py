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
  "project_id": "deft-reporter-477405-c3",
  "private_key_id": "ae7cde4c95c005212cb257c50e945ce3a8a241c5",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCbj7rQY0IhQy4H\nZPFKfWyOyzeipKi18DNtZWMZwo/dxB8SSD9hdNHfuWojk1dM/J8qvkgJJZXzOzdf\n7ZnYgPDHmcwx1HJ0bsXh/5l8AJlb1ENDcfDNxd76w3vFUEcn8KeFdxSguXbZD9u+\n9TO6dQ48M6LpR7x+/ioFy1t9FW+RASOBf46CxYNxrdGdMhdPMAGiLhBounLQ79hu\nu3/W9gZG04zGCPRXOFFK4H3iYA99B01+1v+X56wpjGwe3NYSFK07FlX5/d89K7X8\niLkzb2FWDSpLD7geCxxAcpJntoklDKxiJmme4AyrO8aj2RFAgMLKXXKixMdMFiaD\nI9wiKXBFAgMBAAECggEAAI9MKYqV5Kc/Vp4dsJWbdBKDe+o7aHdVDS8vmqOW+t18\nDCNCDtdS4Li/ZkZxfN53aXC2V7eDA3C5bgkdlkg+frMWS/oIsGY1f9ymROpaEKIP\nyp0689e+ZVasYRdq0rOTcr2s6u7+xOCu+xAamPCgiCoji2VGyxyeO5ea19nYblHj\nZlaFMOsBQBH79P2YNUIHtMBi9k3hnmYMMZy5Ug7sr6/2oN1vqXBEv49Gqw7xTtQG\nEleDpPGv7DmN9jpxmz0MitfLGh6bm/iCZ1rMUi2FOMKL15dFOui2h5JESNy7XM1/\noYhPaMtp43b3ljPaqeOFJCmenNI887BY51TofBw92QKBgQDLkWsPsFMTWfj7Njtv\nt8m6QGBJl5sltkwIJaj1DdH7RUHq6WtqfbCBtVqdYLEjtespcXSPDM8SJHR0JE9J\nABUJFHvWEh4bj/CI1ywz8D8ruMZHbJFYbLrK9UwTiw6o/vgMb6vENMhpivavWkA0\nFbDqwhBMkjFhjmVBpRWnGiIXCQKBgQDDoOujhudXZFVRGUAuFykPmJoYuaRxv4sE\nQgctjAtQPp/n6X6cA44y8eLVU57IW6CwUF0koz0wsvbPsxXkQrgdip2BgydbdFe7\nMVDubvoeIBtkNn8IiT+O0svGQMgLJWrONIeomJ1trXkGqikUWFKVV9id4+thel8G\n8jAPGBECXQKBgQC0RZoO8bIQIAxKwzMNcy+U3e+nHDgLxI0+ZcNjCBMdNq7yTjWO\nv7Hwm96cIgWcvzx6nft/tvMleN0cAQ+pcQYv3VDxOWgqNmTnec2uTSJUILSOicmJ\nCfi9RU9Su0GHTQvzT21IOwoD1Ukx7nWO6mqa6rKubISIhSaMZJpxOcZYqQKBgEh1\nSBIPm4xA+2DIa38m0OyX5yuVRxVijskK88GpB1+3cl7hmyWKI5c3BH9jM4KefYwQ\nmA9D7xwkjUos2MTs+WjnuKMJwwAavYv2HjXSIQ4bcknR7Ydp3oK2DQfnYrDOMRsj\nVcPakyTWhec0C3cfp6btHKyOiNZYDu5xsd9FWLd5AoGAFL6wd//Yrxuw/YaqKRq2\noqZJfAAgxHiGIQ1PrBCNAADlrEr+MfrILlcIpluHJqR823S7CtNaZJmRorqqsgZr\nMDpAhZ+yMnZywVNlrrLYSR/IgBS9O1//Vu9NwPz682jkjHSJhP0wqxVqdlN7Ab69\nQ9ZxDb+SUmHJsHtBMI2FALg=\n-----END PRIVATE KEY-----\n",
  "client_email": "youtube@deft-reporter-477405-c3.iam.gserviceaccount.com",
  "client_id": "100247725945153320941",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/youtube%40deft-reporter-477405-c3.iam.gserviceaccount.com",
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
