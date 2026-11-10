import socket
import threading
import json
import base64
import hashlib
import time

class RealMeshSocketNode:
    def __init__(self, host_ip, port, node_id):
        self.host_ip = host_ip
        self.port = port
        self.node_id = node_id
        self.private_key = hashlib.sha256(f"{node_id}_MASTER_KEY".encode()).hexdigest()
        self.public_key = hashlib.sha256(self.private_key.encode()).hexdigest()[:16]
        self.seen_packets = set()
        self.peers = {}  # تخزين عناوين الـ IP الخاصة بالعقد المجاورة
        self.running = True

    def start_server(self):
        # تشغيل خادم محلي على الجهاز لاستقبال الرسائل من الأجهزة المجاورة
        server_thread = threading.Thread(target=self._listen_loop)
        server_thread.daemon = True
        server_thread.start()
        print(f"[{self.node_id}] الخادم يعمل الآن على {self.host_ip}:{self.port}")

    def _listen_loop(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host_ip, self.port))
        server_socket.listen(5)

        while self.running:
            try:
                client_sock, addr = server_socket.accept()
                data = client_sock.recv(4096).decode('utf-8')
                if data:
                    self.handle_incoming_raw_packet(data)
                client_sock.close()
            except Exception as e:
                break

    def connect_to_peer(self, peer_ip, peer_port, packet_json):
        # إرسال الحزمة لجهاز آخر عبر الشبكة المادية
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)
            s.connect((peer_ip, peer_port))
            s.sendall(packet_json.encode('utf-8'))
            s.close()
            return True
        except Exception:
            return False

    def handle_incoming_raw_packet(self, packet_json):
        # معالجة الحزمة المستلمة وفحصها
        try:
            packet = json.loads(packet_json)
            packet_id = packet["id"]

            if packet_id in self.seen_packets:
                return
            self.seen_packets.add(packet_id)

            if packet["dst"] == self.node_id:
                print(f"\n[📥 وصلتك رسالة جديدة على {self.node_id}]")
                print(f" المرسل: {packet['src']}")
                print(f" المحتوى المشفر (Payload): {packet['payload']}")
                return

            if packet["ttl"] <= 1:
                return

            # تمرير الرسالة (Relay) للعقد المجاورة المسجلة
            packet["ttl"] -= 1
            packet["path"].append(self.node_id)
            updated_json = json.dumps(packet)

            for p_id, (p_ip, p_port) in self.peers.items():
                if p_id != packet["src"]: # عدم إرجاع الرسالة للمرسل
                    self.connect_to_peer(p_ip, p_port, updated_json)

        except Exception as e:
            pass