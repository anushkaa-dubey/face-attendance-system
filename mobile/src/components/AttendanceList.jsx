import React, { useState } from 'react';
import { View, Text, StyleSheet, FlatList, TextInput, TouchableOpacity, RefreshControl } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '../theme/theme';

export const AttendanceList = ({ records = [], onRefresh, refreshing }) => {
  const [searchQuery, setSearchQuery] = useState('');

  const safeRecords = Array.isArray(records) ? records : [];

  const filteredRecords = safeRecords.filter(item => {
    const nameStr = item.person ? String(item.person).toLowerCase() : '';
    const dateStr = item.date ? String(item.date) : '';
    const query = searchQuery.toLowerCase();
    return nameStr.includes(query) || dateStr.includes(query);
  });

  const todayStr = new Date().toISOString().split('T')[0];
  const todayCount = safeRecords.filter(r => r.date === todayStr).length;

  const renderItem = ({ item }) => {
    let formattedTime = 'Recorded';
    if (item.timestamp) {
      try {
        const d = new Date(item.timestamp);
        formattedTime = d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      } catch (e) {
        formattedTime = String(item.timestamp).split('T')[1]?.substring(0, 5) || String(item.timestamp);
      }
    }

    const personName = item.person ? String(item.person) : 'Unknown Employee';

    return (
      <View style={styles.recordItem}>
        <View style={styles.avatarCircle}>
          <Text style={styles.avatarText}>
            {personName.charAt(0).toUpperCase()}
          </Text>
        </View>

        <View style={styles.recordInfo}>
          <Text style={styles.personName}>{personName}</Text>
          <View style={styles.dateRow}>
            <Ionicons name="calendar-outline" size={12} color={theme.colors.textMuted} style={styles.miniIconMargin} />
            <Text style={styles.dateText}>{item.date || todayStr}</Text>
            <Text style={styles.dotSeparator}> • </Text>
            <Ionicons name="time-outline" size={12} color={theme.colors.textMuted} style={styles.miniIconMargin} />
            <Text style={styles.dateText}>{formattedTime}</Text>
          </View>
        </View>

        <View style={styles.presentBadge}>
          <View style={styles.badgeDot} />
          <Text style={styles.presentText}>Present</Text>
        </View>
      </View>
    );
  };

  return (
    <View style={styles.container}>
      {/* Header and Stats */}
      <View style={styles.headerSection}>
        <View style={styles.titleRow}>
          <Text style={styles.sectionTitle}>Attendance Logs</Text>
          <TouchableOpacity 
            style={styles.refreshButton} 
            onPress={onRefresh}
            activeOpacity={0.7}
          >
            <Ionicons name="refresh" size={16} color={theme.colors.primary} />
          </TouchableOpacity>
        </View>

        {/* Stats Row */}
        <View style={styles.statsRow}>
          <View style={[styles.statCard, styles.statCardLeft]}>
            <Text style={styles.statNumber}>{safeRecords.length}</Text>
            <Text style={styles.statLabel}>Total Logs</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={[styles.statNumber, { color: theme.colors.success }]}>{todayCount}</Text>
            <Text style={styles.statLabel}>Today Present</Text>
          </View>
        </View>

        {/* Search Bar */}
        <View style={styles.searchBar}>
          <Ionicons name="search-outline" size={18} color={theme.colors.textMuted} style={styles.searchIconMargin} />
          <TextInput
            style={styles.searchInput}
            placeholder="Search by employee name or date..."
            placeholderTextColor={theme.colors.textMuted}
            value={searchQuery}
            onChangeText={setSearchQuery}
          />
          {searchQuery.length > 0 && (
            <TouchableOpacity onPress={() => setSearchQuery('')}>
              <Ionicons name="close-circle" size={16} color={theme.colors.textMuted} />
            </TouchableOpacity>
          )}
        </View>
      </View>

      {/* Record List */}
      {filteredRecords.length > 0 ? (
        <FlatList
          data={filteredRecords}
          keyExtractor={(item, index) => item.id ? `att-${item.id}` : `rec-${item.person}-${item.date}-${index}`}
          renderItem={renderItem}
          contentContainerStyle={styles.listContent}
          showsVerticalScrollIndicator={false}
          refreshControl={
            <RefreshControl
              refreshing={Boolean(refreshing)}
              onRefresh={onRefresh}
              tintColor={theme.colors.primary}
              colors={[theme.colors.primary]}
            />
          }
        />
      ) : (
        <View style={styles.emptyState}>
          <Ionicons name="clipboard-outline" size={48} color={theme.colors.textMuted} />
          <Text style={styles.emptyTitle}>
            {searchQuery ? 'No matching logs found' : 'No attendance logs recorded yet'}
          </Text>
          <Text style={styles.emptySubtext}>
            {searchQuery ? 'Try searching with another keyword' : 'Mark employee attendance using face recognition above'}
          </Text>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingHorizontal: theme.spacing.md,
  },
  headerSection: {
    marginBottom: theme.spacing.sm,
  },
  titleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: theme.spacing.xs,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: theme.colors.textPrimary,
  },
  refreshButton: {
    padding: 6,
    borderRadius: theme.borderRadius.sm,
    backgroundColor: theme.colors.white,
    borderWidth: 1,
    borderColor: theme.colors.cardBorder,
  },
  statsRow: {
    flexDirection: 'row',
    marginVertical: theme.spacing.sm,
  },
  statCard: {
    flex: 1,
    backgroundColor: theme.colors.white,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.sm + 4,
    borderWidth: 1,
    borderColor: theme.colors.cardBorder,
    alignItems: 'center',
    ...theme.shadows.card,
  },
  statCardLeft: {
    marginRight: theme.spacing.md,
  },
  statNumber: {
    fontSize: 24,
    fontWeight: '800',
    color: theme.colors.primary,
  },
  statLabel: {
    fontSize: 12,
    color: theme.colors.textSecondary,
    fontWeight: '500',
    marginTop: 2,
  },
  searchBar: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.colors.white,
    borderRadius: theme.borderRadius.md,
    paddingHorizontal: theme.spacing.sm + 4,
    paddingVertical: 10,
    borderWidth: 1,
    borderColor: theme.colors.cardBorder,
    marginVertical: theme.spacing.xs,
    ...theme.shadows.card,
  },
  searchIconMargin: {
    marginRight: 6,
  },
  searchInput: {
    flex: 1,
    color: theme.colors.textPrimary,
    fontSize: 14,
    padding: 0,
  },
  listContent: {
    paddingBottom: theme.spacing.xl,
  },
  recordItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.colors.white,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.sm + 4,
    marginBottom: theme.spacing.xs + 4,
    borderWidth: 1,
    borderColor: theme.colors.cardBorder,
    ...theme.shadows.card,
  },
  avatarCircle: {
    width: 42,
    height: 42,
    borderRadius: 21,
    backgroundColor: theme.colors.primaryLight,
    borderWidth: 1,
    borderColor: 'rgba(37, 99, 235, 0.15)',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: theme.spacing.sm,
  },
  avatarText: {
    fontSize: 16,
    fontWeight: '700',
    color: theme.colors.primary,
  },
  recordInfo: {
    flex: 1,
  },
  personName: {
    fontSize: 15,
    fontWeight: '600',
    color: theme.colors.textPrimary,
  },
  dateRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 3,
  },
  miniIconMargin: {
    marginRight: 3,
  },
  dateText: {
    fontSize: 12,
    color: theme.colors.textSecondary,
  },
  dotSeparator: {
    color: theme.colors.textMuted,
    fontSize: 10,
  },
  presentBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.colors.successBg,
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: theme.borderRadius.full,
    borderWidth: 1,
    borderColor: theme.colors.successBorder,
  },
  badgeDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: theme.colors.success,
    marginRight: 5,
  },
  presentText: {
    fontSize: 11,
    fontWeight: '600',
    color: theme.colors.success,
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 40,
  },
  emptyTitle: {
    fontSize: 15,
    fontWeight: '600',
    color: theme.colors.textSecondary,
    marginTop: theme.spacing.sm,
  },
  emptySubtext: {
    fontSize: 12,
    color: theme.colors.textMuted,
    marginTop: 4,
    textAlign: 'center',
  },
});
