import 'dart:io';
import 'package:audioplayers/audioplayers.dart';
import 'package:path_provider/path_provider.dart';

// Stub implementation for platforms that don't support the record package
class AudioService {
  static final AudioService _instance = AudioService._internal();
  factory AudioService() => _instance;
  AudioService._internal();

  final AudioPlayer _player = AudioPlayer();
  bool _isRecording = false;
  String? _currentRecordingPath;

  Future<bool> requestPermissions() async {
    // Windows doesn't need permission handling for now
    return false; // Audio recording not supported on Windows
  }

  Future<bool> hasPermissions() async {
    return false;
  }

  Future<String?> startRecording() async {
    throw UnsupportedError('Audio recording is not supported on Windows desktop');
  }

  Future<String?> stopRecording() async {
    throw UnsupportedError('Audio recording is not supported on Windows desktop');
  }

  Future<void> cancelRecording() async {
    _isRecording = false;
    _currentRecordingPath = null;
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

