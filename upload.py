import customtkinter as ctk
from tkinter import filedialog
import threading
import os
import datetime
import time
import pickle
from PIL import Image, ImageTk, ImageSequence
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def authenticate():
    creds = None
    if os.path.exists("token_upload.pickle"):
        with open("token_upload.pickle", "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token_upload.pickle", "wb") as token:
            pickle.dump(creds, token)
    return build("youtube", "v3", credentials=creds)

def get_video_files_from_folder(folder_path):
    return sorted([f for f in os.listdir(folder_path) if f.lower().endswith(".mp4")])

def generate_schedule_times(start_date, total_videos, times_per_day):
    schedule = []
    current_date = start_date
    index = 0
    for day in range((total_videos + len(times_per_day) - 1) // len(times_per_day)):
        for t in times_per_day:
            if index >= total_videos:
                break
            dt = datetime.datetime.strptime(f"{current_date} {t}", "%Y-%m-%d %H:%M")
            iso_time = dt.isoformat("T") + "Z"
            schedule.append(iso_time)
            index += 1
        current_date += datetime.timedelta(days=1)
    return schedule

def upload_and_schedule(folder, times_per_day, timezone_offset, videos_per_day, update_status, update_stats, stop_spinner):
    youtube = authenticate()
    files = get_video_files_from_folder(folder)
    total_files = len(files)
    if not files:
        update_status("📂 لا توجد فيديوهات mp4 في المجلد المحدد.")
        stop_spinner()
        return

    schedule_times = generate_schedule_times(
        datetime.datetime.now(datetime.timezone.utc).date(), total_files, times_per_day
    )

    for i, filename in enumerate(files):
        video_path = os.path.join(folder, filename)
        title = os.path.splitext(filename)[0]
        publish_time = schedule_times[i]

        # تعديل التوقيت حسب المنطقة الزمنية
        dt_obj = datetime.datetime.strptime(publish_time, "%Y-%m-%dT%H:%M:%SZ")
        dt_obj += datetime.timedelta(hours=timezone_offset)
        publish_time = dt_obj.isoformat("T") + "Z"

        update_status(f"⬆️ رفع: {title}")
        update_stats(f"📁 عدد الفيديوهات: {total_files}\n⬆️ جاري رفع: {filename}\n⏱️ التقدم: {i+1} / {total_files}")

        request_body = {
            "snippet": {
                "title": title,
                "description": "",
                "categoryId": "22"
            },
            "status": {
                "privacyStatus": "private",
                "publishAt": publish_time,
                "selfDeclaredMadeForKids": False
            }
        }

        media_file = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/*")
        upload_request = youtube.videos().insert(
            part="snippet,status",
            body=request_body,
            media_body=media_file
        )

        start_time = time.time()
        response = None
        while response is None:
            status, response = upload_request.next_chunk()
            if status:
                elapsed = time.time() - start_time
                file_size = os.path.getsize(video_path)
                speed = (file_size / 1024 / 1024) / elapsed if elapsed > 0 else 0
                update_stats(f"📁 عدد الفيديوهات: {total_files}\n⬆️ جاري رفع: {filename}\n⏱️ التقدم: {i+1} / {total_files}\n⚡ سرعة الرفع: {speed:.2f} MB/s\n📊 التقدم الحالي: {int(status.progress()*100)}%")

        update_status(f"✅ تم جدولة: {title} في {publish_time}")
        time.sleep(1)

    update_status("🎉 تم رفع وجدولة كل الفيديوهات!")
    update_stats("✅ تم الانتهاء.")
    stop_spinner()

def run_gui():
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    app = ctk.CTk()
    app.geometry("700x630")
    app.title("📺 أداة رفع وجدولة فيديوهات YouTube")

    folder_path = ctk.StringVar()
    videos_per_day = ctk.IntVar(value=5)
    timezone_offset = ctk.IntVar(value=1)
    status_text = ctk.StringVar(value="👋 اختر الإعدادات وابدأ")
    stats_text = ctk.StringVar(value="ℹ️ لم تبدأ العملية بعد.")

    def browse_folder():
        path = filedialog.askdirectory()
        if path:
            folder_path.set(path)

    # تحميل صورة gif
    spinner_frames = []
    try:
        spinner_img = Image.open("loading_spinner.gif")
        spinner_frames = [ImageTk.PhotoImage(f.convert("RGBA")) for f in ImageSequence.Iterator(spinner_img)]
    except:
        pass

    spinner_label = ctk.CTkLabel(app, text="")
    spinner_label.pack(pady=5)
    spinner_running = [False]

    def animate_spinner(count=0):
        if spinner_running[0] and spinner_frames:
            frame = spinner_frames[count % len(spinner_frames)]
            spinner_label.configure(image=frame)
            app.after(100, animate_spinner, count + 1)

    def stop_spinner():
        spinner_running[0] = False
        spinner_label.configure(image="")

    def start_upload():
        times = []
        if time1.get(): times.append("08:00")
        if time2.get(): times.append("11:00")
        if time3.get(): times.append("14:00")
        if time4.get(): times.append("17:00")
        if time5.get(): times.append("20:00")
        if not times:
            status_text.set("❗ اختر على الأقل توقيتًا واحدًا للنشر")
            return
        if not os.path.isdir(folder_path.get()):
            status_text.set("❗ يرجى اختيار مجلد صحيح")
            return
        spinner_running[0] = True
        animate_spinner()
        threading.Thread(
            target=upload_and_schedule,
            args=(folder_path.get(), times, timezone_offset.get(), videos_per_day.get(), status_text.set, stats_text.set, stop_spinner),
            daemon=True
        ).start()

    # واجهة الاستخدام
    ctk.CTkLabel(app, text="📁 مجلد الفيديوهات").pack(pady=5)
    ctk.CTkEntry(app, textvariable=folder_path, width=500).pack()
    ctk.CTkButton(app, text="استعراض...", command=browse_folder).pack(pady=5)

    ctk.CTkLabel(app, text="📅 عدد الفيديوهات يوميًا").pack(pady=5)
    ctk.CTkComboBox(app, variable=videos_per_day, values=[str(i) for i in range(1, 11)]).pack()

    ctk.CTkLabel(app, text="🕒 أوقات النشر (UTC)").pack(pady=5)
    time1 = ctk.CTkCheckBox(app, text="08:00"); time1.pack()
    time2 = ctk.CTkCheckBox(app, text="11:00"); time2.pack()
    time3 = ctk.CTkCheckBox(app, text="14:00"); time3.pack()
    time4 = ctk.CTkCheckBox(app, text="17:00"); time4.pack()
    time5 = ctk.CTkCheckBox(app, text="20:00"); time5.pack()
    time1.select(); time2.select(); time3.select(); time4.select(); time5.select()

    ctk.CTkLabel(app, text="🌍 المنطقة الزمنية (UTC+X)").pack(pady=5)
    ctk.CTkComboBox(app, variable=timezone_offset, values=[str(i) for i in range(-12, 13)]).pack()

    ctk.CTkButton(app, text="🚀 بدء الرفع والجدولة", command=start_upload).pack(pady=15)
    ctk.CTkLabel(app, textvariable=status_text, wraplength=650).pack(pady=10)
    ctk.CTkLabel(app, text="📊 إحصائيات:", anchor="w").pack(pady=(10, 2))
    stats_box = ctk.CTkTextbox(app, height=120, wrap="word")
    stats_box.pack(fill="both", padx=15)
    stats_box.insert("1.0", stats_text.get())
    stats_box.configure(state="disabled")

    def update_stat_box(text):
        stats_box.configure(state="normal")
        stats_box.delete("1.0", "end")
        stats_box.insert("1.0", text)
        stats_box.configure(state="disabled")
        stats_text.set(text)

    stats_text.trace("w", lambda *args: update_stat_box(stats_text.get()))
    app.mainloop()

run_gui()
