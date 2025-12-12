import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
} from 'react-native';
// Note: Voice recognition package may need to be installed separately
// For now, using expo-av for audio recording
// import Voice from '@react-native-voice/voice';
import { Audio } from 'expo-av';
import apiService from '../services/api';

const VoiceRecorder = ({ onTranscriptReceived, onError }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [recording, setRecording] = useState(null);
  const [sound, setSound] = useState(null);
  const [transcript, setTranscript] = useState('');

  useEffect(() => {
    // Request permissions
    (async () => {
      const { status } = await Audio.requestPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission Required', 'Audio recording permission is required');
      }
    })();

    // Cleanup function
    return () => {
      if (sound) {
        sound.unloadAsync();
      }
      if (recording) {
        recording.stopAndUnloadAsync();
      }
    };
  }, []);

  const startRecording = async () => {
    try {
      setTranscript('');
      
      // Start audio recording
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });

      const { recording: newRecording } = await Audio.Recording.createAsync(
        Audio.RecordingOptionsPresets.HIGH_QUALITY
      );
      setRecording(newRecording);
      setIsRecording(true);
    } catch (error) {
      console.error('Error starting recording:', error);
      Alert.alert('Error', 'Failed to start recording');
      if (onError) {
        onError(error.message);
      }
    }
  };

  const stopRecording = async () => {
    try {
      setIsRecording(false);

      if (recording) {
        await recording.stopAndUnloadAsync();
        const uri = recording.getURI();
        setRecording(null);

        // Process audio file
        await processAudioFile(uri);
      }
    } catch (error) {
      console.error('Error stopping recording:', error);
      Alert.alert('Error', 'Failed to stop recording');
    }
  };

  const processAudioFile = async (uri) => {
    setIsProcessing(true);
    try {
      // Send audio to backend for transcription
      const result = await apiService.uploadAudio({ uri });
      
      if (result.transcript) {
        setTranscript(result.transcript);
        if (onTranscriptReceived) {
          onTranscriptReceived(result.transcript);
        }
      }
    } catch (error) {
      console.error('Error processing audio:', error);
      Alert.alert('Error', 'Failed to transcribe audio');
      if (onError) {
        onError(error.message);
      }
    } finally {
      setIsProcessing(false);
    }
  };

  const playRecording = async () => {
    if (!recording) return;

    try {
      const { sound: playbackSound } = await Audio.Sound.createAsync(
        { uri: recording.getURI() },
        { shouldPlay: true }
      );
      setSound(playbackSound);

      playbackSound.setOnPlaybackStatusUpdate((status) => {
        if (status.didJustFinish) {
          playbackSound.unloadAsync();
          setSound(null);
        }
      });
    } catch (error) {
      console.error('Error playing recording:', error);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.recordingContainer}>
        {isRecording && (
          <View style={styles.recordingIndicator}>
            <View style={styles.recordingDot} />
            <Text style={styles.recordingText}>Recording...</Text>
          </View>
        )}
        {isProcessing && (
          <View style={styles.processingContainer}>
            <ActivityIndicator size="small" color="#007AFF" />
            <Text style={styles.processingText}>Processing audio...</Text>
          </View>
        )}
      </View>

      <TouchableOpacity
        style={[styles.button, isRecording && styles.buttonRecording]}
        onPress={isRecording ? stopRecording : startRecording}
        disabled={isProcessing}
      >
        <Text style={styles.buttonText}>
          {isRecording ? 'Stop Recording' : 'Start Recording'}
        </Text>
      </TouchableOpacity>

      {recording && !isRecording && (
        <TouchableOpacity style={styles.playButton} onPress={playRecording}>
          <Text style={styles.playButtonText}>Play Recording</Text>
        </TouchableOpacity>
      )}

      {transcript ? (
        <View style={styles.transcriptContainer}>
          <Text style={styles.transcriptLabel}>Transcript:</Text>
          <Text style={styles.transcriptText}>{transcript}</Text>
        </View>
      ) : null}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 20,
    alignItems: 'center',
  },
  recordingContainer: {
    marginBottom: 20,
    alignItems: 'center',
  },
  recordingIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  recordingDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: '#FF3B30',
    marginRight: 8,
  },
  recordingText: {
    color: '#FF3B30',
    fontSize: 16,
    fontWeight: '600',
  },
  processingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  processingText: {
    marginLeft: 8,
    color: '#007AFF',
    fontSize: 14,
  },
  button: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 30,
    paddingVertical: 15,
    borderRadius: 25,
    minWidth: 200,
    alignItems: 'center',
  },
  buttonRecording: {
    backgroundColor: '#FF3B30',
  },
  buttonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  playButton: {
    marginTop: 15,
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 20,
    backgroundColor: '#34C759',
  },
  playButtonText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
  },
  transcriptContainer: {
    marginTop: 20,
    padding: 15,
    backgroundColor: '#F5F5F5',
    borderRadius: 10,
    width: '100%',
  },
  transcriptLabel: {
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 8,
    color: '#333',
  },
  transcriptText: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
});

export default VoiceRecorder;

