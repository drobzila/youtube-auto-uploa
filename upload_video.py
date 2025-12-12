import os
import json
import random
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# ---------------------------
# إعدادات
# ---------------------------
FOLDER_ID = "1lLKbFPovufWeEkwpCgI3cM-Je-Uee9el"
UPLOADED_JSON = "uploaded.json"

video_titles = [
    "تلاوة خاشعة تلامس القلوب", "صوت يريح القلب والعقل", "آيات تبعث الطمأنينة في النفس",
    "تلاوة عذبة تدمع لها العيون", "استمع لتلاوة تهز المشاعر", "أجمل تلاوة قرآنية مؤثرة جدًا",
    "تلاوة نادرة تبكي القلوب", "صوت ملائكي يشرح الصدر", "خشوع لا يُوصف أثناء التلاوة",
    "تلاوة تهز الوجدان بخشوعها", "صوت يأخذك إلى عالم من السكينة", "أجمل ما تسمع من القرآن الكريم",
    "لحظات روحانية لا تُنسى مع القرآن", "تلاوة تملأ القلب بالنور", "صوت يذكرك بالجنة",
    "راحة نفسية لا توصف مع هذه التلاوة", "آيات تشرح الصدر وتُذهب الهم", "جمال الترتيل وروعة الأداء",
    "صوت يدخل القلب بدون استئذان", "تلاوة هادئة قبل النوم تبعث السكينة",
    "ترتيل يبكي الصخر من الخشوع", "تلاوة مؤثرة بصوت نادر الجمال", "قرآن يلامس الإحساس بعمق",
    "استمع بقلبك لا بأذنك", "تلاوة هادئة تريح أعصابك وتملأك إيمانًا",
    "خشوع لا مثيل له في هذه التلاوة", "صوت كأنه من السماء", "آيات من نور تملأ المكان طمأنينة",
    "تلاوة تذكرك بلقاء الله", "صوت يبكي المستمعين بخشوعه", "لحظة صفاء مع كلام الله",
    "استمع لتلاوة تجعلك تبكي من الخشوع", "تلاوة نادرة من المسجد الحرام", "ترتيل مؤثر من قلب صادق",
    "صوت يبعث السكينة في كل من يسمع", "القرآن شفاء للقلوب — تلاوة مؤثرة جدًا",
    "تلاوة تبعث الطمأنينة في ليل هادئ", "ترتيل ملائكي يلامس الأرواح", "تلاوة من أروع ما يكون",
    "صوت يدخل القلب بلا مقدمات", "قرآن يُتلى بخشوع نادر", "استمع لهذه التلاوة وستشعر بالسكينة",
    "ترتيل يبعث الدموع من شدة الخشوع", "تلاوة تهدئ القلب المرهق", "جمال الصوت وروعة الأداء القرآني",
    "آيات تبكيك من جمالها", "تلاوة مؤثرة جدًا بصوت رائع", "لحظة مع كلام الله تبعث الطمأنينة",
    "صوت مؤثر يذكّرك بالآخرة", "القرآن الكريم بصوت يريح النفس",
    "استمع إلى أجمل ما قرئ من كتاب الله", "صوت نادر في تلاوة تبكي الحجر",
    "تلاوة خاشعة تلامس الروح", "صوت يملأ المكان نورًا وطمأنينة", "ترتيل عذب يهز المشاعر"
]


# ---------------------------
# تحميل JSON
# ---------------------------
def load_uploaded():
    if not os.path.exists(UPLOADED_JSON):
        return []

    with open(UPLOADED_JSON, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return []


def save_uploaded(data):
    with open(UPLOADED_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ---------------------------
# خدمات Google
# ---------------------------
def get_youtube_service():
    creds = Credentials.from_authorized_user_file("credentials.json", ["https://www.googleapis.com/auth/youtube.upload"])
    return build("youtube", "v3", credentials=creds)


def get_drive_service():
    creds = Credentials.from_authorized_user_file("credentials.json", ["https://www.googleapis.com/auth/drive"])
    return build("drive", "v3", credentials=creds)


# ---------------------------
# جلب أول فيديو من درايف
# ---------------------------
def get_first_drive_video(service):
    query = f"'{FOLDER_ID}' in parents and mimeType contains 'video'"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get("files", [])
    return files[0] if files else None


# ---------------------------
# تحميل الفيديو من الدرايف
# ---------------------------
def download_file(service, file_id, filename):
    request = service.files().get_media(fileId=file_id)
    fh = open(filename, "wb")

    downloader = MediaFileUpload if False else None  # نتركه بسيطًا
    downloader = googleapiclient.http.MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        _, done = downloader.next_chunk()

    fh.close()


# ---------------------------
# رفع الفيديو إلى يوتيوب
# ---------------------------
def upload_to_youtube(service, filepath):
    title = random.choice(video_titles)

    body = {
        "snippet": {"title": title},
        "status": {"privacyStatus": "public"}
    }

    media = MediaFileUpload(filepath, chunksize=-1, resumable=True)

    request = service.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    response = request.execute()
    return title, response["id"]


# ---------------------------
# حذف فيديو من الدرايف
# ---------------------------
def delete_drive_file(service, file_id):
    service.files().delete(fileId=file_id).execute()


# ---------------------------
# MAIN
# ---------------------------
def main():
    print("🚀 بدء العملية...")

    drive = get_drive_service()
    yt = get_youtube_service()

    uploaded = load_uploaded()

    # جلب أول فيديو
    file = get_first_drive_video(drive)
    if not file:
        print("📂 لا توجد ملفات لرفعها.")
        return

    print(f"📥 تحميل: {file['name']}")
    download_file(drive, file["id"], file["name"])

    print("⬆️ رفع إلى يوتيوب...")
    title, video_id = upload_to_youtube(yt, file["name"])
    print(f"✅ Uploaded: {title} | ID: {video_id}")

    # تسجيل JSON
    uploaded.append({
        "file": file["name"],
        "video_id": video_id,
        "title": title
    })
    save_uploaded(uploaded)

    # حذف الفيديو من Drive
    delete_drive_file(drive, file["id"])
    os.remove(file["name"])

    print("🧹 تم حذف الفيديو من الدرايف والملف المحلي.")
    print("🏁 Done!")


if __name__ == "__main__":
    main()
