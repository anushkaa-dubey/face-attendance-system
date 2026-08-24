import React, { useState } from 'react';
import { View, Text, StyleSheet, Modal, TextInput, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '../theme/theme';
import { getApiUrl, setApiUrl } from '../api/config';

export const ServerConfigModal = ({ visible, onClose, onSaved }) => {
  const [urlInput, setUrlInput] = useState(getApiUrl());

  const handleSave = () => {
    const updated = setApiUrl(urlInput);
    setUrlInput(updated);
    if (onSaved) onSaved(updated);
    onClose();
  };

  const applyPreset = (presetUrl) => {
    setUrlInput(presetUrl);
  };

  return (
    <Modal
      visible={Boolean(visible)}
      transparent={true}
      animationType="fade"
      onRequestClose={onClose}
    >
      <View style={styles.modalOverlay}>
        <View style={styles.modalContent}>
          <View style={styles.modalHeader}>
            <View style={styles.headerTitleRow}>
              <Ionicons name="server-outline" size={22} color={theme.colors.primary} style={styles.headerIconMargin} />
              <Text style={styles.modalTitle}>Backend Server Config</Text>
            </View>
            <TouchableOpacity onPress={onClose}>
              <Ionicons name="close" size={22} color={theme.colors.textMuted} />
            </TouchableOpacity>
          </View>

          <Text style={styles.description}>
            Enter the FastAPI backend base URL. Default is http://localhost:8000.
          </Text>

          <Text style={styles.inputLabel}>Server Base URL</Text>
          <View style={styles.inputWrapper}>
            <TextInput
              style={styles.input}
              value={urlInput}
              onChangeText={setUrlInput}
              placeholder="http://localhost:8000"
              placeholderTextColor={theme.colors.textMuted}
              autoCapitalize="none"
              autoCorrect={false}
            />
          </View>

          <Text style={styles.presetLabel}>Quick Presets:</Text>
          <View style={styles.presetsRow}>
            <TouchableOpacity
              style={styles.presetChip}
              onPress={() => applyPreset('http://localhost:8000')}
            >
              <Text style={styles.presetText}>Localhost</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.presetChip}
              onPress={() => applyPreset('http://10.0.2.2:8000')}
            >
              <Text style={styles.presetText}>Android Emulator</Text>
            </TouchableOpacity>
          </View>

          <View style={styles.buttonRow}>
            <TouchableOpacity
              style={styles.cancelButton}
              onPress={onClose}
            >
              <Text style={styles.cancelText}>Cancel</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.saveButton}
              onPress={handleSave}
            >
              <Text style={styles.saveText}>Save & Connect</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(15, 23, 42, 0.6)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: theme.spacing.md,
  },
  modalContent: {
    width: '100%',
    maxWidth: 420,
    backgroundColor: theme.colors.white,
    borderRadius: theme.borderRadius.lg,
    padding: theme.spacing.lg,
    borderWidth: 1,
    borderColor: theme.colors.cardBorder,
    ...theme.shadows.card,
  },
  modalHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: theme.spacing.sm,
  },
  headerTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  headerIconMargin: {
    marginRight: 6,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: theme.colors.textPrimary,
  },
  description: {
    fontSize: 13,
    color: theme.colors.textSecondary,
    marginBottom: theme.spacing.md,
  },
  inputLabel: {
    fontSize: 12,
    fontWeight: '600',
    color: theme.colors.textSecondary,
    marginBottom: 6,
  },
  inputWrapper: {
    backgroundColor: theme.colors.inputBg,
    borderRadius: theme.borderRadius.md,
    borderWidth: 1,
    borderColor: theme.colors.cardBorder,
    paddingHorizontal: theme.spacing.sm + 2,
    marginBottom: theme.spacing.md,
  },
  input: {
    height: 44,
    color: theme.colors.textPrimary,
    fontSize: 14,
  },
  presetLabel: {
    fontSize: 12,
    fontWeight: '600',
    color: theme.colors.textMuted,
    marginBottom: 8,
  },
  presetsRow: {
    flexDirection: 'row',
    marginBottom: theme.spacing.lg,
  },
  presetChip: {
    backgroundColor: theme.colors.primaryLight,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: theme.borderRadius.full,
    borderWidth: 1,
    borderColor: 'rgba(37, 99, 235, 0.2)',
    marginRight: 8,
  },
  presetText: {
    fontSize: 12,
    color: theme.colors.primary,
    fontWeight: '600',
  },
  buttonRow: {
    flexDirection: 'row',
  },
  cancelButton: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: theme.borderRadius.md,
    alignItems: 'center',
    backgroundColor: theme.colors.inputBg,
    borderWidth: 1,
    borderColor: theme.colors.cardBorder,
    marginRight: theme.spacing.sm,
  },
  cancelText: {
    color: theme.colors.textSecondary,
    fontWeight: '600',
  },
  saveButton: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: theme.borderRadius.md,
    alignItems: 'center',
    backgroundColor: theme.colors.primary,
    ...theme.shadows.button,
  },
  saveText: {
    color: theme.colors.white,
    fontWeight: '700',
  },
});
