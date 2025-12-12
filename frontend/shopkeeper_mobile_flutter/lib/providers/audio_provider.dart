import 'package:flutter/foundation.dart';
import '../services/audio_service.dart';
import '../services/api_service.dart';

class AudioProvider with ChangeNotifier {
  final AudioService _audioService = AudioService();
  final ApiService _apiService = ApiService();

  bool _isRecording = false;
  String? _recordingPath;
  String? _transcription;
  bool _isTranscribing = false;

  bool get isRecording => _isRecording;
  String? get recordingPath => _recordingPath;
  String? get transcription => _transcription;
  bool get isTranscribing => _isTranscribing;

  Future<void> startRecording() async {
    try {
      _recordingPath = await _audioService.startRecording();
      _isRecording = true;
      notifyListeners();
    } catch (e) {
      rethrow;
    }
  }

  Future<String?> stopRecording() async {
    try {
      _recordingPath = await _audioService.stopRecording();
      _isRecording = false;
      notifyListeners();
      return _recordingPath;
    } catch (e) {
      _isRecording = false;
      notifyListeners();
      rethrow;
    }
  }

  Future<void> cancelRecording() async {
    await _audioService.cancelRecording();
    _recordingPath = null;
    _isRecording = false;
    notifyListeners();
  }

  Future<void> transcribeAudio() async {
    if (_recordingPath == null) return;

    _isTranscribing = true;
    notifyListeners();

    try {
      _transcription = await _apiService.uploadAudioAndTranscribe(_recordingPath!);
    } catch (e) {
      rethrow;
    } finally {
      _isTranscribing = false;
      notifyListeners();
    }
  }

  void clearTranscription() {
    _transcription = null;
    notifyListeners();
  }
}

