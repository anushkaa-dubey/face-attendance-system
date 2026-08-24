import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '../theme/theme';

export const Header = ({ isOnline, onOpenConfig }) => {
  return (
    <View style={styles.container}>
      <View style={styles.titleContainer}>
        <View style={styles.logoBadge}>
          <Ionicons name="scan-circle" size={28} color={theme.colors.primary} />
        </View>
        <View style={styles.titleCol}>
          <Text style={styles.title}>Face Attendance</Text>
          <Text style={styles.subtitle}>AI Employee Recognition</Text>
        </View>
      </View>

      <View style={styles.actionsContainer}>
        <TouchableOpacity 
          style={[styles.statusBadge, isOnline ? styles.onlineBadge : styles.offlineBadge]} 
          onPress={onOpenConfig}
          activeOpacity={0.8}
        >
          <View style={[styles.statusDot, isOnline ? styles.onlineDot : styles.offlineDot]} />
          <Text style={[styles.statusText, isOnline ? styles.onlineText : styles.offlineText]}>
            {isOnline ? 'Online' : 'Offline'}
          </Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={styles.settingsButton} 
          onPress={onOpenConfig}
          activeOpacity={0.7}
        >
          <Ionicons name="settings-outline" size={20} color={theme.colors.textSecondary} />
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: theme.spacing.md,
    paddingTop: theme.spacing.sm,
    paddingBottom: theme.spacing.sm,
    backgroundColor: theme.colors.white,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.cardBorder,
  },
  titleContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  logoBadge: {
    width: 42,
    height: 42,
    borderRadius: theme.borderRadius.md,
    backgroundColor: theme.colors.primaryLight,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: 'rgba(37, 99, 235, 0.15)',
    marginRight: 10,
  },
  titleCol: {
    justifyContent: 'center',
  },
  title: {
    fontSize: 18,
    fontWeight: '700',
    color: theme.colors.textPrimary,
    letterSpacing: -0.2,
  },
  subtitle: {
    fontSize: 11,
    color: theme.colors.textSecondary,
    fontWeight: '500',
    marginTop: 1,
  },
  actionsContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: theme.borderRadius.full,
    marginRight: 8,
  },
  onlineBadge: {
    backgroundColor: theme.colors.successBg,
    borderWidth: 1,
    borderColor: theme.colors.successBorder,
  },
  offlineBadge: {
    backgroundColor: theme.colors.dangerBg,
    borderWidth: 1,
    borderColor: theme.colors.dangerBorder,
  },
  statusDot: {
    width: 7,
    height: 7,
    borderRadius: 4,
    marginRight: 6,
  },
  onlineDot: {
    backgroundColor: theme.colors.success,
  },
  offlineDot: {
    backgroundColor: theme.colors.danger,
  },
  statusText: {
    fontSize: 12,
    fontWeight: '600',
  },
  onlineText: {
    color: theme.colors.success,
  },
  offlineText: {
    color: theme.colors.danger,
  },
  settingsButton: {
    width: 36,
    height: 36,
    borderRadius: theme.borderRadius.md,
    backgroundColor: theme.colors.inputBg,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: theme.colors.cardBorder,
  },
});
