import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import AudioRecorderPlayer from 'react-native-audio-recorder-player';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { COLORS, SIZES } from '../utils/constants';

const audioRecorderPlayer = new AudioRecorderPlayer();

const AudioPlayer = ({ audioUri }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentPosition, setCurrentPosition] = useState(0);
  const [duration, setDuration] = useState(0);

  useEffect(() => {
    if (audioUri) {
      audioRecorderPlayer.addPlayBackListener((e) => {
        setCurrentPosition(e.currentPosition);
        setDuration(e.duration);
        if (e.currentPosition === e.duration) {
          setIsPlaying(false);
          audioRecorderPlayer.stopPlayer();
        }
        return;
      });
    }

    return () => {
      audioRecorderPlayer.removePlayBackListener();
      if (isPlaying) {
        audioRecorderPlayer.stopPlayer();
      }
    };
  }, [audioUri]);

  const togglePlayback = async () => {
    if (!audioUri) return;

    try {
      if (isPlaying) {
        await audioRecorderPlayer.pausePlayer();
        setIsPlaying(false);
      } else {
        if (currentPosition === 0) {
          await audioRecorderPlayer.startPlayer(audioUri);
        } else {
          await audioRecorderPlayer.resumePlayer();
        }
        setIsPlaying(true);
      }
    } catch (error) {
      console.error('Error toggling playback:', error);
    }
  };

  const stopPlayback = async () => {
    try {
      await audioRecorderPlayer.stopPlayer();
      setIsPlaying(false);
      setCurrentPosition(0);
    } catch (error) {
      console.error('Error stopping playback:', error);
    }
  };

  const formatTime = (milliseconds) => {
    const totalSeconds = Math.floor(milliseconds / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  };

  if (!audioUri) {
    return null;
  }

  return (
    <View style={styles.container}>
      <TouchableOpacity
        style={styles.playButton}
        onPress={togglePlayback}
        activeOpacity={0.7}
      >
        <Icon
          name={isPlaying ? 'pause' : 'play-arrow'}
          size={24}
          color={COLORS.primary}
        />
      </TouchableOpacity>
      
      <View style={styles.timeContainer}>
        <Text style={styles.timeText}>
          {formatTime(currentPosition)} / {formatTime(duration)}
        </Text>
      </View>

      <TouchableOpacity
        style={styles.stopButton}
        onPress={stopPlayback}
        activeOpacity={0.7}
      >
        <Icon name="stop" size={24} color={COLORS.error} />
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.surface,
    padding: SIZES.padding,
    borderRadius: SIZES.borderRadius,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  playButton: {
    marginRight: SIZES.padding,
  },
  timeContainer: {
    flex: 1,
  },
  timeText: {
    fontSize: 14,
    color: COLORS.text,
  },
  stopButton: {
    marginLeft: SIZES.padding,
  },
});

export default AudioPlayer;



