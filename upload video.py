from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os

# تحديد نطاق الوصول
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

# مسار ملف الـ OAuth
CLIENT_SECRET_FILE = os.getenv("YOUTUBE_CLIENT_SECRET_PATH")  # تأكد من إضافة المسار من البيئة أو المتغيرات

# إنشاء خدمة YouTube
def get_authenticated_service():
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRET_FILE, SCOPES
    )
    credentials = flow.run_local_server()  # فتح نافذة متصفح لتسجيل الدخول
    return build("youtube", "v3", credentials=credentials)

# الحصول على آخر 10 فيديوهات شورت من قناة يوتيوب
def get_last_10_shorts_videos(channel_id, youtube_service):
    # استخدم videos().list للبحث عن الفيديوهات
    request = youtube_service.videos().list(
        part="snippet,contentDetails",
        channelId=channel_id,
        maxResults=10,  # الحد الأقصى للنتائج
        order="date"  # ترتيب الفيديوهات حسب التاريخ
    )
    
    response = request.execute()

    videos = response.get("items", [])
    
    if not videos:
        print("No videos found.")
        return

    print("Last 10 Shorts videos:")
    shorts_videos = []
    for video in videos:
        video_id = video['id']
        video_details = youtube_service.videos().list(
            part="contentDetails",
            id=video_id
        ).execute()

        # التحقق من مدة الفيديو
        duration = video_details['items'][0]['contentDetails']['duration']
        
        # إذا كانت مدة الفيديو أقل من 60 ثانية، فهو فيديو شورت
        if 'PT' in duration and 'S' in duration:
            seconds = int(duration.split('PT')[1].split('S')[0])
            if seconds <= 60:
                title = video['snippet']['title']
                shorts_videos.append(title)

    if shorts_videos:
        for title in shorts_videos:
            print(f"- {title}")
    else:
        print("No Shorts videos found.")

# الدالة الرئيسية
def main():
    youtube_service = get_authenticated_service()

    # معرّف القناة (يمكنك تغييره وفقًا للقناة التي تريد استخراج الفيديوهات منها)
    channel_id = "UCHYJMygtSl60pThu6AUgeOw"  # استبدل بهذا المعرّف

    # الحصول على آخر 10 فيديوهات شورت من القناة
    get_last_10_shorts_videos(channel_id, youtube_service)

if __name__ == "__main__":
    main()
