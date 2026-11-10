import zlib
import base64

class DataCompressor:
    @staticmethod
    def compress_message(text_message):
        # ضغط النص باستخدام zlib ثم تحويله لـ Base64 لنقله بسهولة داخل الـ JSON
        raw_bytes = text_message.encode('utf-8')
        compressed_bytes = zlib.compress(raw_bytes, level=9)
        return base64.b64encode(compressed_bytes).decode('utf-8')

    @staticmethod
    def decompress_message(compressed_base64):
        # فك الضغط واستعادة النص الأصلي بدقة
        decoded_bytes = base64.b64decode(compressed_base64.encode('utf-8'))
        original_bytes = zlib.decompress(decoded_bytes)
        return original_bytes.decode('utf-8')

# تجربة سريعة للضغط والفك
sample_msg = "هذه رسالة تجريبية سرية للغاية لاختبار كفاءة الضغط الفائق في الشبكات اللامركزية الصعبة!"
compressed = DataCompressor.compress_message(sample_msg)
restored = DataCompressor.decompress_message(compressed)

print(f"الحجم قبل الضغط: {len(sample_msg)} بايت")
print(f"الحجم بعد الضغط والترميز: {len(compressed)} بايت")
print(f"النص المستعاد بنجاح: {restored}")