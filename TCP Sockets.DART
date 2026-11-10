import 'dart:io';
import 'dart:convert';

class MeshNetworkManager {
  final String nodeId;
  final int port;
  ServerSocket? _server;
  final List<String> receivedMessages = [];

  MeshNetworkManager({required this.nodeId, required this.port});

  // 1. بدء تشغيل السيرفر المحلي على الموبايل للاستماع للرسائل
  Future<void> startServer(Function(String) onMessageReceived) async {
    try {
      _server = await ServerSocket.bind(InternetAddress.anyIPv4, port);
      print('[$nodeId] الخادم يعمل بنجاح على المنفذ $port');
      
      _server!.listen((Socket client) {
        client.listen((data) {
          String rawPacket = utf8.decode(data);
          onMessageReceived(rawPacket);
        });
      });
    } catch (e) {
      print('خطأ في تشغيل السيرفر: $e');
    }
  }

  // 2. إرسال الرسالة لجهاز مجاور عبر الـ IP الخاص به
  Future<bool> sendMessageToPeer(String peerIp, int peerPort, String packetJson) async {
    try {
      Socket socket = await Socket.connect(peerIp, peerPort, timeout: const Duration(seconds: 3));
      socket.write(packetJson);
      await socket.flush();
      socket.destroy();
      return true;
    } catch (e) {
      print('فشل إرسال الرسالة للجهاز: $e');
      return false;
    }
  }

  // إيقاف السيرفر
  void stopServer() {
    _server?.close();
  }
}