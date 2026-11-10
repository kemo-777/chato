import time

class BackgroundPowerManager:
    def __init__(self, wake_interval_seconds=5, sleep_interval_seconds=25):
        self.wake_interval = wake_interval_seconds       # فترة الاستماع النشط للشبكة
        self.sleep_interval = sleep_interval_seconds     # فترة السبات لتوفير استهلاك البطارية
        self.is_active = True

    def run_background_cycle(self):
        print("[Battery Manager] خدمة الخلفية لشبكة الـ Mesh تعمل بكفاءة...")
        while self.is_active:
            # 1. حالة الاستماع النشط لاستقبال وتمرير الرسائل
            print(f"-> [استيقاظ] فحص القنوات المحيطة لمدة {self.wake_interval} ثوانٍ...")
            time.sleep(self.wake_interval)

            # 2. تفعيل وضع توفير الطاقة (Duty Cycling)
            print(f"-> [سبات عميق] إيقاف الراديو مؤقتاً لتوفير طاقة البطارية لمدة {self.sleep_interval} ثانية...")
            time.sleep(self.sleep_interval)

    def stop(self):
        self.is_active = False

# تشغيل نموذج إدارة البطارية
# manager = BackgroundPowerManager()
# manager.run_background_cycle()