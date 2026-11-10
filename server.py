import asyncio
import json
import logging

# إعداد نظام تسجيل الأحداث (Logging) لمتابعة الاتصالات والحزم لحظة بلحظة
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')

class AdvancedMeshServer:
    def __init__(self, host='0.0.0.0', port=4040):
        self.host = host
        self.port = port
        self.connected_nodes = {}  # جدول لتخزين العقد النشطة وعناوينها

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        addr = writer.get_extra_info('peername')
        logging.info(f"تم استقبال اتصال جديد من الجهاز: {addr}")

        try:
            while True:
                data = await reader.read(4096)
                if not data:
                    break
                
                packet_raw = data.decode('utf-8')
                packet = json.loads(packet_raw)
                
                node_id = packet.get("src")
                destination = packet.get("dst")
                
                # تسجيل العقدة النشطة في الشبكة
                if node_id:
                    self.connected_nodes[node_id] = writer

                logging.info(f"توجيه حزمة من [{node_id}] إلى الوجهة [{destination}]")

                # توجيه الحزمة لو العقدة المستهدفة متصلة مباشرة بالسيرفر
                if destination in self.connected_nodes:
                    target_writer = self.connected_nodes[destination]
                    target_writer.write(data)
                    await target_writer.drain()
                    logging.info(f"تم تسليم الحزمة بنجاح إلى العقدة: {destination}")
                else:
                    logging.warning(f"الوجهة [{destination}] غير متصلة حالياً بالسيرفر، جارٍ تفعيل نظام الـ Mesh Relay...")

        except asyncio.CancelledError:
            pass
        except Exception as e:
            logging.error(f"خطأ في معالجة العقدة {addr}: {e}")
        finally:
            logging.info(f"انقطع الاتصال مع الجهاز: {addr}")
            # إزالة العقدة من القائمة عند انقطاعها
            for n_id, w in list(self.connected_nodes.items()):
                if w == writer:
                    del self.connected_nodes[n_id]
            writer.close()
            await writer.wait_closed()

    async def start(self):
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        addr = server.sockets[0].getsockname()
        logging.info(f"السيرفر الأقوى يعمل الآن بكفاءة على العنوان {addr}")

        async with server:
            await server.serve_forever()

if __name__ == "__main__":
    mesh_server = AdvancedMeshServer()
    try:
        asyncio.run(mesh_server.start())
    except KeyboardInterrupt:
        logging.info("تم إيقاف السيرفر يدويفاً بواسطة المسؤول.")