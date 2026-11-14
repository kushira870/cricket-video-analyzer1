
import 'package:http/http.dart' as http;
import 'package:video_thumbnail/video_thumbnail.dart';

import 'dart:io';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:video_player/video_player.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const CricketApp());
}

class CricketApp extends StatelessWidget {
  const CricketApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Cricket Video Analyzer',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.green,
          brightness: Brightness.dark,
        ),
        useMaterial3: true,
      ),
      home: const CricketHome(),
    );
  }
}

class CricketHome extends StatefulWidget {
  const CricketHome({super.key});

  @override
  State<CricketHome> createState() => _CricketHomeState();
}

class _CricketHomeState extends State<CricketHome> {
String? selectedVideoPath;
bool analyzing = false;

static const String aiBackendUrl =
    'https://YOUR-BACKEND-URL/analyze';

  final ImagePicker picker = ImagePicker();
  final TextEditingController playerController =
      TextEditingController();
  final TextEditingController notesController =
      TextEditingController();

  VideoPlayerController? videoController;
  List<Map<String, String>> reports = [];
  bool loading = false;

  @override
  void initState() {
    super.initState();
    loadReports();
  }

  Future<void> loadReports() async {
    final prefs = await SharedPreferences.getInstance();
    final saved = prefs.getString('cricket_reports');

    if (saved != null) {
      try {
        final decoded = jsonDecode(saved) as List;
        if (!mounted) return;
        setState(() {
          reports = decoded.map((item) {
            return Map<String, String>.from(item as Map);
          }).toList();
        });
      } catch (_) {
        // Ignore invalid saved data.
      }
    }
  }

  Future<void> selectVideo() async {
    try {
      final video = await picker.pickVideo(
        source: ImageSource.gallery,
      );

      if (video == null) return;

      setState(() => loading = true);

      final controller = VideoPlayerController.networkUrl(
        Uri.parse('file://${video.path}'),
      );

      // Use a file controller for local Android videos.
      await controller.dispose();

      final localController =
          VideoPlayerController.file(
        // dart:io File is used below.
        File(video.path),
      );

      await localController.initialize();

      if (!mounted) {
        await localController.dispose();
        return;
      }

      final oldController = videoController;
      setState(() {
        videoController = localController;
        loading = false; 
selectedVideoPath = video.path;
        
      });
      await oldController?.dispose();
    } catch (e) {
      if (!mounted) return;
      setState(() => loading = false);
      showMessage('Video loading failed: $e');
    }
  }

  void showMessage(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message)),
    );
  }

  Future<void> saveAnalysis() async {
    final player = playerController.text.trim();
    final notes = notesController.text.trim();

    if (player.isEmpty || notes.isEmpty) {
      showMessage('Enter player name and analysis notes');
      return;
    }

    final report = {
      'player': player,
      'notes': notes,
      'date': DateTime.now().toLocal().toString().split('.')[0],
    };

    setState(() {
      reports.insert(0, report);
    });

    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(
      'cricket_reports',
      jsonEncode(reports),
    );

    notesController.clear();
    showMessage('Analysis saved successfully');
  }

  Future<void> deleteReport(int index) async {
    setState(() => reports.removeAt(index));
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(
      'cricket_reports',
      jsonEncode(reports),
    );
  }

  @override
  void dispose() {
    videoController?.dispose();
    playerController.dispose();
    notesController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final controller = videoController;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Cricket Video Analyzer'),
        centerTitle: true,
        backgroundColor: Colors.green.shade900,
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Icon(
            Icons.sports_cricket,
            size: 65,
            color: Colors.greenAccent,
          ),
          const SizedBox(height: 8),
          const Text(
            'CRICKET VIDEO ANALYZER',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 21,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 20),
          ElevatedButton.icon(
            onPressed: loading ? null : selectVideo,
            icon: const Icon(Icons.video_library),
            label: const Text('Select Cricket Video'),
          ),
          const SizedBox(height: 16),
          if (loading)
            const Center(
              child: CircularProgressIndicator(),
            ),
          if (controller != null &&
              controller.value.isInitialized) ...[
            AspectRatio(
              aspectRatio: controller.value.aspectRatio,
              child: VideoPlayer(controller),
            ),
            const SizedBox(height: 8),
            VideoProgressIndicator(
              controller,
              allowScrubbing: true,
              padding: const EdgeInsets.symmetric(
                vertical: 8,
              ),
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                IconButton(
                  onPressed: () async {
                    final current = controller.value.position;
                    final target =
                        current - const Duration(seconds: 5);
                    await controller.seekTo(
                      target.isNegative
                          ? Duration.zero
                          : target,
                    );
                  },
                  icon: const Icon(Icons.replay_5),
                ),
                IconButton(
                  onPressed: () async {
                    if (controller.value.isPlaying) {
                      await controller.pause();
                    } else {
                      await controller.play();
                    }
                    setState(() {});
                  },
                  icon: Icon(
                    controller.value.isPlaying
                        ? Icons.pause_circle
                        : Icons.play_circle,
                    size: 42,
                  ),
                ),
                IconButton(
                  onPressed: () async {
                    await controller.seekTo(
                      controller.value.position +
                          const Duration(seconds: 5),
                    );
                  },
                  icon: const Icon(Icons.forward_5),
                ),
              ],
            ),
          ],
          const SizedBox(height: 24),
          const Text(
            'Player Analysis',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: playerController,
            decoration: const InputDecoration(
              labelText: 'Player Name',
              border: OutlineInputBorder(),
              prefixIcon: Icon(Icons.person),
            ),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: notesController,
            maxLines: 5,
            decoration: const InputDecoration(
              labelText: 'Batting / Bowling Analysis',
              hintText:
                  'Example: Footwork, timing, '
                  'bat swing, bowling action...',
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 12),
          ElevatedButton.icon(
            onPressed: saveAnalysis,
            icon: const Icon(Icons.save),
            label: const Text('Save Analysis'),
          ),
          const SizedBox(height: 24),
          const Text(
            'Saved Analysis Reports',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          if (reports.isEmpty)
            const Padding(
              padding: EdgeInsets.all(16),
              child: Text('No saved reports yet'),
            ),
          ...List.generate(reports.length, (index) {
            final report = reports[index];
            return Card(
              child: ListTile(
                title: Text(report['player'] ?? ''),
                subtitle: Text(
                  '${report['notes'] ?? ''}\n'
                  '${report['date'] ?? ''}',
                ),
                isThreeLine: true,
                trailing: IconButton(
                  icon: const Icon(Icons.delete),
                  onPressed: () => deleteReport(index),
                ),
              ),
            );
          }),
        ],
      ),
    );
  }
}

