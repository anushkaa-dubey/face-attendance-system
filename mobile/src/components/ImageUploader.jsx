import React from 'react';
import { View, Text, StyleSheet, Image, TouchableOpacity, ActivityIndicator, Alert } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '../theme/theme';

export const ImageUploader = ({ selectedImage, setSelectedImage, onRecognize, isLoading }) => {

  const pickImageFromGallery = async () => {
    try {
      const permissionResult = await ImagePicker.requestMediaLibraryPermissionsAsync();
      
      if (!permissionResult.granted) {
        Alert.alert('Permission Needed', 'Access to media library is required to select employee photos.');
        return;
      }

      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [1, 1],
        quality: 0.8,
      });

      if (!result.canceled && result.assets && result.assets.length > 0) {
        setSelectedImage(result.assets[0]);
      }
    } catch (error) {
      console.error('Gallery picker error:', error);
      Alert.alert('Error', 'Failed to open image gallery');
    }
  };

  const takePhotoFromCamera = async () => {
    try {
      const permissionResult = await ImagePicker.requestCameraPermissionsAsync();

      if (!permissionResult.granted) {
        Alert.alert('Permission Needed', 'Camera permission is required to capture photos.');
        return;
      }

      const result = await ImagePicker.launchCameraAsync({
        allowsEditing: true,
        aspect: [1, 1],
        quality: 0.8,
      });

      if (!result.canceled && result.assets && result.assets.length > 0) {
        setSelectedImage(result.assets[0]);
      }
    } catch (error) {
      console.error('Camera picker error:', error);
      Alert.alert('Error', 'Failed to open camera');
    }
  };

  const clearImage = () => {
    setSelectedImage(null);
  };

  return (
    <View style={styles.card}>
      <Text style={styles.cardTitle}>Employee Verification</Text>
      <Text style={styles.cardSubtitle}>Upload or capture a face photo to mark attendance</Text>

      {selectedImage ? (
        <View style={styles.previewContainer}>
          <Image source={{ uri: selectedImage.uri }} style={styles.previewImage} />
          
          <TouchableOpacity 
            style={styles.clearBadge} 
            onPress={clearImage}
            disabled={isLoading}
            activeOpacity={0.8}
          >
            <Ionicons name="close-circle" size={26} color={theme.colors.danger} />
          </TouchableOpacity>

          <View style={styles.imageOverlayInfo}>
            <Ionicons name="checkmark-circle" size={14} color={theme.colors.primary} style={styles.badgeIconMargin} />
            <Text style={styles.imageInfoText}>Photo Ready</Text>
          </View>
        </View>
      ) : (
        <View style={styles.uploadPlaceholder}>
          <View style={styles.iconCircle}>
            <Ionicons name="cloud-upload-outline" size={32} color={theme.colors.primary} />
          </View>
          <Text style={styles.placeholderText}>No photo selected yet</Text>
          <Text style={styles.placeholderSubtext}>Select an image from gallery or take a picture</Text>
        </View>
      )}

      {/* Action Buttons */}
      <View style={styles.buttonRow}>
        <TouchableOpacity
          style={[styles.actionButton, styles.galleryButton]}
          onPress={pickImageFromGallery}
          disabled={isLoading}
          activeOpacity={0.85}
        >
          <Ionicons name="image-outline" size={20} color={theme.colors.white} style={styles.btnIconMargin} />
          <Text style={styles.galleryButtonText}>Open Gallery</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.actionButton, styles.cameraButton]}
          onPress={takePhotoFromCamera}
          disabled={isLoading}
          activeOpacity={0.85}
        >
          <Ionicons name="camera-outline" size={20} color={theme.colors.textPrimary} style={styles.btnIconMargin} />
          <Text style={styles.cameraButtonText}>Take Photo</Text>
        </TouchableOpacity>
      </View>

      {/* Recognize & Mark Attendance Primary Action */}
      {selectedImage && (
        <TouchableOpacity
          style={[
            styles.submitButton,
            isLoading && styles.submitButtonDisabled
          ]}
          onPress={onRecognize}
          disabled={isLoading}
          activeOpacity={0.85}
        >
          {isLoading ? (
            <View style={styles.loadingRow}>
              <ActivityIndicator size="small" color={theme.colors.white} style={styles.btnIconMargin} />
              <Text style={styles.submitButtonText}>Analyzing Face...</Text>
            </View>
          ) : (
            <View style={styles.loadingRow}>
              <Ionicons name="checkmark-done-circle" size={22} color={theme.colors.white} style={styles.btnIconMargin} />
              <Text style={styles.submitButtonText}>Mark Attendance</Text>
            </View>
          )}
        </TouchableOpacity>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: theme.colors.white,
    borderRadius: theme.borderRadius.lg,
    padding: theme.spacing.md + 2,
    borderWidth: 1,
    borderColor: theme.colors.cardBorder,
    marginHorizontal: theme.spacing.md,
    marginVertical: theme.spacing.sm,
    ...theme.shadows.card,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: theme.colors.textPrimary,
    marginBottom: 2,
  },
  cardSubtitle: {
    fontSize: 13,
    color: theme.colors.textSecondary,
    marginBottom: theme.spacing.md,
  },
  previewContainer: {
    position: 'relative',
    alignSelf: 'center',
    width: 180,
    height: 180,
    borderRadius: theme.borderRadius.lg,
    overflow: 'hidden',
    borderWidth: 2,
    borderColor: theme.colors.primary,
    marginBottom: theme.spacing.md,
    backgroundColor: '#F1F5F9',
  },
  previewImage: {
    width: '100%',
    height: '100%',
    resizeMode: 'cover',
  },
  clearBadge: {
    position: 'absolute',
    top: 6,
    right: 6,
    backgroundColor: theme.colors.white,
    borderRadius: 15,
    elevation: 2,
  },
  imageOverlayInfo: {
    position: 'absolute',
    bottom: 6,
    left: 6,
    backgroundColor: 'rgba(255, 255, 255, 0.92)',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: theme.borderRadius.sm,
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: theme.colors.cardBorder,
  },
  badgeIconMargin: {
    marginRight: 4,
  },
  imageInfoText: {
    fontSize: 11,
    color: theme.colors.textPrimary,
    fontWeight: '600',
  },
  uploadPlaceholder: {
    height: 150,
    borderRadius: theme.borderRadius.md,
    borderWidth: 1.5,
    borderColor: '#CBD5E1',
    borderStyle: 'dashed',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#F8FAFC',
    marginBottom: theme.spacing.md,
    padding: theme.spacing.sm,
  },
  iconCircle: {
    width: 52,
    height: 52,
    borderRadius: 26,
    backgroundColor: theme.colors.primaryLight,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: theme.spacing.xs,
  },
  placeholderText: {
    fontSize: 14,
    fontWeight: '600',
    color: theme.colors.textPrimary,
  },
  placeholderSubtext: {
    fontSize: 12,
    color: theme.colors.textMuted,
    marginTop: 2,
  },
  buttonRow: {
    flexDirection: 'row',
  },
  actionButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    borderRadius: theme.borderRadius.md,
  },
  galleryButton: {
    backgroundColor: theme.colors.primary,
    marginRight: 8,
  },
  galleryButtonText: {
    color: theme.colors.white,
    fontWeight: '600',
    fontSize: 14,
  },
  cameraButton: {
    backgroundColor: theme.colors.inputBg,
    borderWidth: 1,
    borderColor: theme.colors.cardBorder,
  },
  cameraButtonText: {
    color: theme.colors.textPrimary,
    fontWeight: '600',
    fontSize: 14,
  },
  submitButton: {
    backgroundColor: theme.colors.primaryDark,
    borderRadius: theme.borderRadius.md,
    paddingVertical: 14,
    alignItems: 'center',
    marginTop: theme.spacing.md,
    ...theme.shadows.button,
  },
  submitButtonDisabled: {
    opacity: 0.6,
  },
  submitButtonText: {
    color: theme.colors.white,
    fontWeight: '700',
    fontSize: 15,
    letterSpacing: 0.2,
  },
  btnIconMargin: {
    marginRight: 6,
  },
  loadingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
});
