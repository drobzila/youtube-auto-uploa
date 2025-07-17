import os
import random
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import datetime
import time

# Client Secrets and Tokens
DRIVE_CLIENT_ID = os.getenv('DRIVE_CLIENT_ID')
DRIVE_CLIENT_SECRET = os.getenv('DRIVE_CLIENT_SECRET')
DRIVE_REFRESH_TOKEN = os.getenv('DRIVE_REFRESH_TOKEN')
YOUTUBE_CLIENT_ID = os.getenv('YOUTUBE_CLIENT_ID')
YOUTUBE_CLIENT_SECRET = os.getenv('YOUTUBE_CLIENT_SECRET')
YOUTUBE_REFRESH_TOKEN = os.getenv('YOUTUBE_REFRESH_TOKEN')

# Google Drive Folder ID
FOLDER_ID = '1_iPtcfFs3TpusMr9THwTc31SWtLtwccZ'  # Folder ID for videos

# Scopes
SCOPES = ['https://www.googleapis.com/auth/drive.readonly', 'https://www.googleapis.com/auth/youtube.upload']

# File paths
VIDEO_IDS_FILE = 'uploaded_video_ids.pickle'  # To keep track of uploaded video IDs
VIDEO_LIST_FILE = 'video_list.pickle'  # To keep track of the list of videos to avoid repeats

# Authenticate with Google Drive API
def authenticate_drive():
    creds = None
    if os.path.exists('drive_token.json'):
        creds = Credentials.from_authorized_user_file('drive_token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        with open('drive_token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

# Authenticate with YouTube API
def authenticate_youtube():
    creds = None
    if os.path.exists('youtube_token.json'):
        creds = Credentials.from_authorized_user_file('youtube_token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'youtube_client_secrets.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        with open('youtube_token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

# Fetch video list from Google Drive
def download_files_from_drive(creds, folder_id):
    drive_service = build('drive', 'v3', credentials=creds)
    query = f"'{folder_id}' in parents and mimeType='video/mp4'"  # Get only mp4 videos
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get('files', [])
    if not items:
        print('No videos found in the folder.')
    else:
        print(f"Found {len(items)} videos.")
        return items
    return []

# Upload video to YouTube
def upload_video(creds, video_file, title, description):
    youtube_service = build('youtube', 'v3', credentials=creds)

    # Set up media upload
    media = MediaFileUpload(video_file, resumable=True, mimetype="video/mp4")

    request = youtube_service.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": ["auto-upload", "test"],  # Add more tags as needed
            },
            "status": {
                "privacyStatus": "private",  # You can change this to "public" or "unlisted"
            },
        },
        media_body=media,
    )

    # Upload the video
    response = request.execute()
    print(f"Video uploaded successfully! Video ID: {response['id']}")
    return response['id']

# Check if the video has already been uploaded
def is_video_uploaded(video_id):
    if os.path.exists(VIDEO_IDS_FILE):
        with open(VIDEO_IDS_FILE, 'rb') as file:
            uploaded_ids = pickle.load(file)
            if video_id in uploaded_ids:
                return True
    return False

# Save the video ID to avoid re-uploading
def save_video_id(video_id):
    uploaded_ids = []
    if os.path.exists(VIDEO_IDS_FILE):
        with open(VIDEO_IDS_FILE, 'rb') as file:
            uploaded_ids = pickle.load(file)
    uploaded_ids.append(video_id)
    with open(VIDEO_IDS_FILE, 'wb') as file:
        pickle.dump(uploaded_ids, file)

# Get a random video from the drive folder
def get_random_video(videos):
    return random.choice(videos)

# Schedule videos for upload
def schedule_videos(videos):
    times = ["12:00", "16:00", "20:00"]  # Set the times for video upload
    for i, video in enumerate(videos[:3]):
        video_file = video['name']
        title = video['name']
        description = f"Automatically uploaded at {times[i]}"
        video_id = upload_video(youtube_creds, video_file, title, description)
        save_video_id(video_id)

if __name__ == "__main__":
    # Authenticate with both Google Drive and YouTube
    drive_creds = authenticate_drive()
    youtube_creds = authenticate_youtube()

    # Download videos from Google Drive
    videos = download_files_from_drive(drive_creds, FOLDER_ID)

    if videos:
        # Schedule videos for uploading
        schedule_videos(videos)
    else:
        print("No videos to upload.")
