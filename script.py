# script.py

log_file = 'log.txt'  # اسم الملف الذي سيتم إضافة السجلات فيه

# كتابة النص في الملف
with open(log_file, 'a') as f:  # فتح الملف في وضع الإضافة (append)
    f.write("Hello, World!\n")  # كتابة "Hello, World!" في الملف

print("Hello, World!")  # الطباعة في GitHub Actions لعرضها في السجلات
