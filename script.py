import time

log_file = 'log.txt'

# سيكتب السكربت 5 مرات في الدقيقة
for _ in range(5):  # يكتب 5 مرات
    with open(log_file, 'a') as f:
        f.write("Hello, World!\n")
    print("Hello, World!")  # الطباعة في الـ console
    time.sleep(12)  # الانتظار لمدة 12 ثانية قبل الكتابة مرة أخرى
