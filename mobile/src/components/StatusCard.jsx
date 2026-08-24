import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '../theme/theme';

export const StatusCard = ({ result }) => {
  if (!result) return null;

  const { recognized, person, similarity, message } = result;

  const isSuccess = Boolean(recognized);
  const isAlreadyMarked = message && typeof message === 'string' && message.toLowerCase().includes('already marked');
  
  let bannerColor = theme.colors.danger;
  let bannerBg = theme.colors.dangerBg;
  let bannerBorder = theme.colors.dangerBorder;
  let iconName = "alert-circle";

  if (isSuccess) {
    bannerColor = isAlreadyMarked ? theme.colors.warning : theme.colors.success;
    bannerBg = isAlreadyMarked ? theme.colors.warningBg : theme.colors.successBg;
    bannerBorder = isAlreadyMarked ? theme.colors.warningBorder : theme.colors.successBorder;
    iconName = isAlreadyMarked ? "time-outline" : "checkmark-circle";
  } else if (message && typeof message === 'string' && message.includes('No face')) {
    bannerColor = theme.colors.warning;
    bannerBg = theme.colors.warningBg;
    bannerBorder = theme.colors.warningBorder;
    iconName = "eye-off-outline";
  }

  const confidencePercentage = similarity ? (similarity * 100).toFixed(1) : null;
  const personDisplayName = person ? String(person) : 'Unknown';

  return (
    <View style={[styles.container, { borderColor: bannerBorder }]}>
      <View style={[styles.headerBanner, { backgroundColor: bannerBg, borderBottomColor: bannerBorder }]}>
        <Ionicons name={iconName} size={22} color={bannerColor} style={styles.bannerIconMargin} />
        <Text style={[styles.bannerTitle, { color: bannerColor }]}>
          {message || (recognized ? 'Attendance Marked' : 'Verification Failed')}
        </Text>
      </View>

      {recognized ? (
        <View style={styles.contentBody}>
          <View style={styles.personRow}>
            <View style={styles.avatar}>
              <Text style={styles.avatarText}>
                {personDisplayName.charAt(0).toUpperCase()}
              </Text>
            </View>
            <View style={styles.personDetails}>
              <Text style={styles.personLabel}>Employee Name</Text>
              <Text style={styles.personName}>{personDisplayName}</Text>
            </View>
          </View>

          {confidencePercentage && (
            <View style={styles.metaRow}>
              <View style={styles.metaBadge}>
                <Ionicons name="sparkles-outline" size={14} color={theme.colors.primary} style={styles.badgeIconMargin} />
                <Text style={styles.metaText}>{confidencePercentage}% Match</Text>
              </View>
              <View style={styles.metaBadge}>
                <Ionicons name="calendar-outline" size={14} color={theme.colors.textSecondary} style={styles.badgeIconMargin} />
                <Text style={styles.metaText}>Today</Text>
              </View>
            </View>
          )}
        </View>
      ) : (
        <View style={styles.contentBody}>
          <Text style={styles.failureDescription}>
            {message === "Unknown person" 
              ? "The face detected does not match any registered employee in the gallery database." 
              : (message || "Failed to verify identity.")}
          </Text>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: theme.colors.white,
    borderRadius: theme.borderRadius.lg,
    overflow: 'hidden',
    borderWidth: 1,
    marginHorizontal: theme.spacing.md,
    marginVertical: theme.spacing.sm,
    ...theme.shadows.card,
  },
  headerBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: theme.spacing.md,
    paddingVertical: theme.spacing.sm + 2,
    borderBottomWidth: 1,
  },
  bannerIconMargin: {
    marginRight: 8,
  },
  bannerTitle: {
    fontSize: 15,
    fontWeight: '700',
    flex: 1,
  },
  contentBody: {
    padding: theme.spacing.md,
  },
  personRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  avatar: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: theme.colors.primaryLight,
    borderWidth: 1,
    borderColor: 'rgba(37, 99, 235, 0.2)',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: theme.spacing.md,
  },
  avatarText: {
    fontSize: 22,
    fontWeight: '700',
    color: theme.colors.primary,
  },
  personDetails: {
    flex: 1,
  },
  personLabel: {
    fontSize: 12,
    color: theme.colors.textSecondary,
    fontWeight: '500',
  },
  personName: {
    fontSize: 18,
    fontWeight: '700',
    color: theme.colors.textPrimary,
    marginTop: 1,
  },
  metaRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: theme.spacing.md,
    paddingTop: theme.spacing.sm,
    borderTopWidth: 1,
    borderTopColor: theme.colors.cardBorder,
  },
  metaBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.colors.inputBg,
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: theme.borderRadius.full,
    borderWidth: 1,
    borderColor: theme.colors.cardBorder,
    marginRight: theme.spacing.sm,
  },
  badgeIconMargin: {
    marginRight: 4,
  },
  metaText: {
    fontSize: 12,
    color: theme.colors.textSecondary,
    fontWeight: '600',
  },
  failureDescription: {
    fontSize: 13,
    color: theme.colors.textSecondary,
    lineHeight: 18,
  },
});
