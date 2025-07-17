import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# تحديد نطاق الوصول
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

# استرجاع الـ client_secret من البيئة
CLIENT_SECRET_FILE = json.loads(os.getenv('YOUTUBE_CLIENT20SECRET'))  # استخدام Secret من GitHub

# إنشاء خدمة YouTube
def get_authenticated_service():
    flow = InstalledAppFlow.from_client_config(
        CLIENT_SECRET_FILE, SCOPES
    )
    credentials = flow.run_local_server()  # فتح نافذة متصفح لتسجيل الدخول
    return build("youtube", "v3", credentials=credentials)

# الحصول على آخر 10 فيديوهات شورت من قناة يوتيوب
def get_last_10_shorts_videos(channel_id, youtube_service):
    request = youtube_service.search().list(
        part="snippet",
        channelId=channel_id,
        maxResults=10,
        type="video",
        order="date"  # ترتيب النتائج حسب الأحدث
    )
    response = request.execute()

    videos = response.get("items", [])
    
    if not videos:
        print("No videos found.")
        return

    print("Last 10 Shorts videos:")
    shorts_videos = []
    for video in videos:
        video_id = video['id']['videoId']
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
