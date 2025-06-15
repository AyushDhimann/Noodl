import 'dart:io';
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:frontend/providers/quiz_page_provider.dart';
import 'package:http/http.dart' as http;
import 'package:path_provider/path_provider.dart';
import 'package:audioplayers/audioplayers.dart';
import 'package:provider/provider.dart';

AudioPlayer? _ttsPlayer;

/// Plays TTS using Azure and notifies when audio is finished.
Future<void> playTtsFromFile(String text, BuildContext context) async {
  const subscriptionKey = '05d5fe68a97847948613e036d56f4131';
  const region = 'eastus';
  final endpoint = Uri.parse('https://$region.tts.speech.microsoft.com/cognitiveservices/v1');

  final ssml = '''
<speak version="1.0" xml:lang="en-US">
  <voice xml:lang="en-US" xml:gender="Female" name="en-US-AvaMultilingualNeural">
    $text
  </voice>
</speak>
''';

  try {
    final response = await http.post(
      endpoint,
      headers: {
        'Ocp-Apim-Subscription-Key': subscriptionKey,
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3',
        'User-Agent': 'flutter-app',
      },
      body: ssml,
    );

    if (response.statusCode == 200) {
      final Uint8List audioBytes = response.bodyBytes;

      final tempDir = await getTemporaryDirectory();
      final filePath = '${tempDir.path}/tts_audio.mp3';
      final audioFile = File(filePath);
      await audioFile.writeAsBytes(audioBytes);

      if (await audioFile.length() == 0) {
        throw Exception('TTS audio file is empty.');
      }

      // Stop previous playback
      await _ttsPlayer?.stop();
      _ttsPlayer = AudioPlayer();

      // ✅ Listen for playback completion
      _ttsPlayer!.onPlayerComplete.listen((event) {
        context.mounted?
        Provider.of<QuizPageProvider>(context, listen: false).ttsCompleteTrue():null;
        
        print('✅ Audio playback complete!');
        // Optional: you can call setState, trigger next action, etc.
      });

      await _ttsPlayer!.play(DeviceFileSource(audioFile.path));
    } else {
      throw Exception('TTS failed: ${response.statusCode} ${response.reasonPhrase}');
    }
  } catch (e) {
    print('❌ Error during TTS playback: $e');
  }
}

/// Stops current TTS playback.
Future<void> stopTtsAudio() async {
  if (_ttsPlayer != null) {
    await _ttsPlayer!.stop();
    await _ttsPlayer!.release(); // optional: free resources
    _ttsPlayer = null;
    print('⏹️ Audio stopped.');
  }
}
