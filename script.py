import time

log_file = 'log.txt'

# سيعمل السكربت فقط لمدة دقيقة واحدة ويدخل في حلقة يكتب فيها "Hello, World!" كل 5 ثوانٍ
end_time = time.time() + 60  # تحديد الوقت لإنهاء السكربت بعد دقيقة واحدة

while time.time() < end_time:
    with open(log_file, 'a') as f:
        f.write("Hello, World!\n")
    print("Hello, World!")  # الطباعة في الـ console

    time.sleep(5)  # الانتظار لمدة 5 ثوانٍ قبل الكتابة مرة أخرى
