import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class HomePage extends StatefulWidget {
  const HomePage({super.key});
  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  final String piIp = "localhost"; // Replace with Raspberry Pi LAN IP for real devices
  String status = "Loading...";
  Timer? _timer;

  Future<void> getStatus() async {
    try {
      final res = await http.get(Uri.parse("http://$piIp:5000/status"));
      final data = jsonDecode(res.body);
      setState(() => status = (data["person_detected"] ?? false)
          ? "👤 Person → Light ${data["relay"] ?? 'Unknown'}"
          : "🚫 None → Light ${data["relay"] ?? 'Unknown'}");
    } catch (e) {
      setState(() => status = "Error: $e");
    }
  }

  @override
  void initState() {
    super.initState();
    getStatus();

    // Auto-refresh image every 500ms
    _timer = Timer.periodic(const Duration(milliseconds: 500), (_) {
      setState(() {}); // Triggers rebuild and reloads image
      getStatus(); // Optional: refresh status automatically
    });
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    String imageUrl = "http://$piIp:5000/video?${DateTime.now().millisecondsSinceEpoch}";

    return Scaffold(
      appBar: AppBar(title: const Text("Electricity Saver")),
      body: Column(
        children: [
          Expanded(
            child: Image.network(
              imageUrl,
              fit: BoxFit.cover,
              errorBuilder: (_, __, ___) =>
                  const Center(child: Text("❌ Video not available")),
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(12),
            child: Column(
              children: [
                Text(status, style: const TextStyle(fontSize: 18)),
                const SizedBox(height: 8),
                ElevatedButton(onPressed: getStatus, child: const Text("Refresh")),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
