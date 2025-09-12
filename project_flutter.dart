import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

void main() => runApp(const MyApp());

class MyApp extends StatelessWidget {
  const MyApp({super.key});
  @override
  Widget build(BuildContext context) => const MaterialApp(home: HomePage());
}

class HomePage extends StatefulWidget {
  const HomePage({super.key});
  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  final String piIp = "localhost"; // Flask server runs locally
  String status = "Loading...";

  Future<void> getStatus() async {
    try {
      final res = await http.get(Uri.parse("http://$piIp:5000/status"));
      final data = jsonDecode(res.body);
      setState(() => status = data["person_detected"]
          ? "👤 Person → Light ${data["relay"]}"
          : "🚫 None → Light ${data["relay"]}");
    } catch (e) {
      setState(() => status = "Error: $e");
    }
  }

  @override
  void initState() {
    super.initState();
    getStatus();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Electricity Saver")),
      body: Column(
        children: [
          Expanded(
            child: Image.network(
              "http://$piIp:5000/video",
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
