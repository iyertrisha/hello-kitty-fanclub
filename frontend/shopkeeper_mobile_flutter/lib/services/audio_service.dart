import 'dart:io';
import 'package:audioplayers/audioplayers.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart' as path;

class AudioService {
  static final AudioService _instance = AudioService._internal();
  factory AudioService() => _instance;
  AudioService._internal();

  final AudioPlayer _player = AudioPlayer();
  bool _isRecording = false;
  String? _currentRecordingPath;

  Future<bool> requestPermissions() async {
    if (Platform.isWindows) {
      return false; // Not supported on Windows
    }
    final status = await Permission.microphone.request();
    return status.isGranted;
  }

  Future<bool> hasPermissions() async {
    if (Platform.isWindows) {
      return false; // Not supported on Windows
    }
    final status = await Permission.microphone.status;
    return status.isGranted;
  }

  Future<String?> startRecording() async {
    if (Platform.isWindows) {
      throw UnsupportedError('Audio recording is not supported on Windows desktop. Please use Android or iOS for voice recording features.');
    }
    
    throw UnsupportedError('Audio recording requires the record package. Please uncomment it in pubspec.yaml for mobile platforms.');
  }

  Future<String?> stopRecording() async {
    if (!_isRecording) return null;
    _isRecording = false;
    return _currentRecordingPath;
  }

  Future<void> cancelRecording() async {
    if (_isRecording) {
      _isRecording = false;
      if (_currentRecordingPath != null && await File(_currentRecordingPath!).exists()) {
        await File(_currentRecordingPath!).delete();
      }
      _currentRecordingPath = null;
    }
  }

  bool get isRecording => _isRecording;

  String? get currentRecordingPath => _currentRecordingPath;

  // Playback
  Future<void> playAudio(String filePath) async {
    try {
      await _player.play(DeviceFileSource(filePath));
    } catch (e) {
      throw Exception('Failed to play audio: $e');
    }
  }

  Future<void> stopPlayback() async {
    await _player.stop();
  }

  Future<void> pausePlayback() async {
    await _player.pause();
  }

  Future<void> resumePlayback() async {
    await _player.resume();
  }

  Stream<Duration> get onPositionChanged => _player.onPositionChanged;
  Stream<Duration> get onDurationChanged => _player.onDurationChanged;
  Stream<PlayerState> get onPlayerStateChanged => _player.onPlayerStateChanged;

  Future<void> dispose() async {
    await _player.dispose();
  }
}

