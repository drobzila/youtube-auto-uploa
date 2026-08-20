# YouTube Auto Uploader

أداة Python لأتمتة رفع وإدارة فيديوهات YouTube، مع دعم التعامل مع الفيديوهات المحلية وGoogle Drive وتتبع الفيديوهات التي تم رفعها.

## المميزات
- رفع الفيديوهات إلى YouTube عبر YouTube Data API.
- إدارة ملفات الفيديو ومتابعة حالة الرفع.
- دعم التكامل مع Google Drive.
- إمكانية تشغيل المشروع من خلال Python أو GitHub Actions.

## المتطلبات
- Python 3.10+
- YouTube Data API v3
- Google credentials المناسبة للعمليات المطلوبة.
- المتطلبات الموجودة في `requirements.txt`.

## التثبيت
```bash
git clone https://github.com/drobzila/youtube-auto-uploa.git
cd youtube-auto-uploa
pip install -r requirements.txt
```

## الإعداد
ضع مفاتيح API وبيانات الاعتماد في متغيرات البيئة أو ملفات محلية غير مرفوعة إلى Git.

**لا ترفع ملفات Service Account أو OAuth tokens أو أي مفاتيح سرية إلى المستودع.**

## التشغيل
```bash
python script.py
```

قد تختلف نقطة التشغيل حسب المهمة؛ راجع `script.py` وملفات الرفع المساعدة.

## بنية المشروع
- `script.py` — الأتمتة الرئيسية.
- `youtube.py` — وظائف مرتبطة بـ YouTube.
- `upload_video.py` — رفع الفيديوهات.
- `telegram_to_drive.py` — التعامل مع ملفات Telegram وGoogle Drive.
- `requirements.txt` — مكتبات Python.
- `.github/` — إعدادات GitHub Actions.

## الأمان
إذا ظهرت بيانات اعتماد Google أو مفاتيح API في Git history، قم بإلغائها وتدويرها فورًا ثم أزلها من المستودع والتاريخ عند الحاجة.

## الترخيص
لم يتم تحديد ترخيص للمشروع بعد.
