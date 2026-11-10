import 'dart:io';
import 'dart:convert';
import 'package:flutter/material.dart';

void main() => runApp(const MeshChatApp());

class MeshChatApp extends StatelessWidget {
  const MeshChatApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'MeshChat - Offline Secure',
      theme: ThemeData.dark().copyWith(
        scaffoldBackgroundColor: const Color(0xFF121212),
        primaryColor: Colors.deepPurple,
      ),
      home: const ChatScreen(),
    );
  }
}

class ChatScreen extends StatefulWidget {
  const ChatScreen({Key? key}) : super(key: key);

  @override
  _ChatScreenState createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _msgController = TextEditingController();
  final TextEditingController _ipController = TextEditingController();
  final List<String> _messages = ["أهلاً بك في نظام الـ Mesh اللامركزي الآمن!"];
  
  ServerSocket? _serverSocket;
  final int _port = 4040; // منفذ الاتصال الموحد للشبكة

  @override
  void initState() {
    super.initState();
    _startLocalServer(); // تشغيل السيرفر المحلي فور فتح التطبيق
  }

  // 1. تشغيل السيرفر لاستقبال الرسائل من الأجهزة الأخرى
  Future<void> _startLocalServer() async {
    try {
      _serverSocket = await ServerSocket.bind(InternetAddress.anyIPv4, _port);
      _serverSocket!.listen((Socket client) {
        client.listen((data) {
          String incomingMsg = utf8.decode(data);
          setState(() {
            _messages.add("مستلم: $incomingMsg");
          });
        });
      });
      setState(() {
        _messages.add("[النظام] تم تفعيل عقدة الاستقبال المحلية بنجاح.");
      });
    } catch (e) {
      setState(() {
        _messages.add("[خطأ] تعذر فتح السيرفر المحلي: $e");
      });
    }
  }

  // 2. إرسال الرسالة لجهاز آخر عبر الـ IP الخاص به بدون إنترنت
  Future<void> _sendMessage() async {
    String text = _msgController.text.trim();
    String targetIp = _ipController.text.trim();

    if (text.isEmpty || targetIp.isEmpty) return;

    try {
      // الاتصال المباشر بالجهاز المجاور عبر السوكيت
      Socket socket = await Socket.connect(targetIp, _port, timeout: const Duration(seconds: 3));
      socket.write(text);
      await socket.flush();
      socket.destroy();

      setState(() {
        _messages.add("أنت (إلى $targetIp): $text");
      });
      _msgController.clear();
    } catch (e) {
      setState(() {
        _messages.add("[فشل الإرسال] تأكد من اتصال الـ Wi-Fi المحلي مع الجهاز الآخر.");
      });
    }
  }

  @override
  void dispose() {
    _serverSocket?.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('MeshChat - شبكة ميدانية آمنة'),
        backgroundColor: const Color(0xFF1F1F1F),
      ),
      body: Column(
        children: [
          // شريط إدخال IP الجهاز المجاور
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: TextField(
              controller: _ipController,
              decoration: const InputDecoration(
                labelText: 'أدخل IP الجهاز المجاور (مثال: 192.168.4.2)',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.network_cell),
              ),
            ),
          ),
          // قائمة الشات والرسائل
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(8.0),
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                return Container(
                  margin: const EdgeInsets.symmetric(vertical: 4.0),
                  padding: const EdgeInsets.all(10.0),
                  decoration: BoxDecoration(
                    color: const Color(0xFF2C2C2C),
                    borderRadius: BorderRadius.circular(8.0),
                  ),
                  child: Text(_messages[index], style: const TextStyle(color: Colors.white)),
                );
              },
            ),
          ),
          // شريط كتابة الرسالة وزر الإرسال
          Container(
            padding: const EdgeInsets.all(8.0),
            color: const Color(0xFF1F1F1F),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _msgController,
                    decoration: const InputDecoration(
                      hintText: 'اكتب رسالتك هنا...',
                      border: InputBorder.none,
                    ),
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.send, color: Colors.deepPurpleAccent),
                  onPressed: _sendMessage,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}