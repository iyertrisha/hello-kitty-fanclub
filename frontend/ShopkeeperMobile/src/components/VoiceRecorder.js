import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
  Platform,
  PermissionsAndroid,
} from 'react-native';
import AudioRecorderPlayer from 'react-native-audio-recorder-player';
import RNFS from 'react-native-fs';
import { COLORS, SIZES } from '../utils/constants';
import { apiService } from '../services/api';
import Icon from 'react-native-vector-icons/MaterialIcons';

const audioRecorderPlayer = new AudioRecorderPlayer();

const VoiceRecorder = ({ onTranscriptReceived, onError }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [recordingPath, setRecordingPath] = useState(null);
  const [transcript, setTranscript] = useState('');
  const [recordTime, setRecordTime] = useState('00:00');

  useEffect(() => {
    return () => {
      // Cleanup on unmount
      if (isRecording) {
        stopRecording();
      }
    };
  }, []);

  const requestPermissions = async () => {
    if (Platform.OS === 'android') {
      try {
        const granted = await PermissionsAndroid.requestMultiple([
          PermissionsAndroid.PERMISSIONS.RECORD_AUDIO,
          PermissionsAndroid.PERMISSIONS.WRITE_EXTERNAL_STORAGE,
          PermissionsAndroid.PERMISSIONS.READ_EXTERNAL_STORAGE,
        ]);
        
        if (
          granted['android.permission.RECORD_AUDIO'] !== PermissionsAndroid.RESULTS.GRANTED ||
          granted['android.permission.WRITE_EXTERNAL_STORAGE'] !== PermissionsAndroid.RESULTS.GRANTED
        ) {
          Alert.alert('Permission Required', 'Audio recording permissions are required');
          return false;
        }
        return true;
      } catch (err) {
        console.warn(err);
        return false;
      }
    }
    return true;
  };

  const startRecording = async () => {
    try {
      const hasPermission = await requestPermissions();
      if (!hasPermission) return;

      setTranscript('');
      setRecordTime('00:00');

      const path = Platform.select({
        ios: `${RNFS.DocumentDirectoryPath}/recording_${Date.now()}.m4a`,
        android: `${RNFS.DocumentDirectoryPath}/recording_${Date.now()}.m4a`,
      });

      const audioSet = {
        AudioEncoderAndroid: 3, // AAC
        AudioSourceAndroid: 1, // MIC
        AVModeIOSOption: 'measurement',
        AVEncoderAudioQualityKeyIOS: 'high',
        AVNumberOfChannelsKeyIOS: 2,
        AVFormatIDKeyIOS: 'aac',
      };

      const uri = await audioRecorderPlayer.startRecorder(path, audioSet);
      audioRecorderPlayer.addRecordBackListener((e) => {
        setRecordTime(audioRecorderPlayer.mmssss(Math.floor(e.currentPosition)));
        return;
      });

      setRecordingPath(uri);
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
      const result = await audioRecorderPlayer.stopRecorder();
      audioRecorderPlayer.removeRecordBackListener();
      setIsRecording(false);
      
      if (result) {
        await processAudioFile(result);
      }
    } catch (error) {
      console.error('Error stopping recording:', error);
      Alert.alert('Error', 'Failed to stop recording');
      if (onError) {
        onError(error.message);
      }
    }
  };

  const processAudioFile = async (uri) => {
    setIsProcessing(true);
    try {
      // Read file as base64
      const base64Audio = await RNFS.readFile(uri, 'base64');
      
      // Determine MIME type
      const mimeType = uri.endsWith('.m4a') 
        ? 'audio/m4a' 
        : uri.endsWith('.mp3')
        ? 'audio/mp3'
        : 'audio/m4a';

      // Create audio file object
      const audioFile = {
        uri: uri,
        type: mimeType,
        name: `recording_${Date.now()}.m4a`,
        base64: base64Audio,
      };

      // Send audio to backend for transcription
      const result = await apiService.uploadAudio(audioFile);
      
      if (result && result.transcript) {
        setTranscript(result.transcript);
        if (onTranscriptReceived) {
          onTranscriptReceived(result.transcript);
        }
      } else {
        throw new Error('No transcript received from server');
      }
    } catch (error) {
      console.error('Error processing audio:', error);
      Alert.alert(
        'Transcription Error', 
        error.message || 'Failed to transcribe audio. Please try again or enter details manually.'
      );
      if (onError) {
        onError(error.message || 'Failed to transcribe audio');
      }
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.recordingContainer}>
        {isRecording && (
          <View style={styles.recordingIndicator}>
            <View style={styles.recordingDot} />
            <Text style={styles.recordingText}>Recording... {recordTime}</Text>
          </View>
        )}
        {isProcessing && (
          <View style={styles.processingContainer}>
            <ActivityIndicator size="small" color={COLORS.primary} />
            <Text style={styles.processingText}>Processing audio...</Text>
          </View>
        )}
      </View>

      <TouchableOpacity
        style={[styles.button, isRecording && styles.buttonRecording]}
        onPress={isRecording ? stopRecording : startRecording}
        disabled={isProcessing}
      >
        <Icon 
          name={isRecording ? 'stop' : 'mic'} 
          size={24} 
          color={isRecording ? COLORS.error : COLORS.onPrimary} 
        />
        <Text style={styles.buttonText}>
          {isRecording ? 'Stop Recording' : 'Start Recording'}
        </Text>
      </TouchableOpacity>

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
    marginVertical: SIZES.margin,
  },
  recordingContainer: {
    marginBottom: SIZES.margin,
    minHeight: 40,
  },
  recordingIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: SIZES.padding,
    backgroundColor: COLORS.error + '20',
    borderRadius: SIZES.borderRadius,
  },
  recordingDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: COLORS.error,
    marginRight: 8,
  },
  recordingText: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.error,
  },
  processingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: SIZES.padding,
  },
  processingText: {
    marginLeft: 8,
    fontSize: 14,
    color: COLORS.textSecondary,
  },
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: COLORS.primary,
    padding: SIZES.padding,
    borderRadius: SIZES.borderRadius,
    marginBottom: SIZES.margin,
  },
  buttonRecording: {
    backgroundColor: COLORS.error,
  },
  buttonText: {
    color: COLORS.onPrimary,
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
  },
  transcriptContainer: {
    backgroundColor: COLORS.surface,
    padding: SIZES.padding,
    borderRadius: SIZES.borderRadius,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  transcriptLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.text,
    marginBottom: 8,
  },
  transcriptText: {
    fontSize: 16,
    color: COLORS.text,
    lineHeight: 24,
  },
});

export default VoiceRecorder;



