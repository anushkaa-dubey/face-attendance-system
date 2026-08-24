import React, { useState, useEffect, useCallback } from 'react';
import { 
  StyleSheet, 
  Text, 
  View, 
  ScrollView, 
  TouchableOpacity, 
  Alert,
  ActivityIndicator
} from 'react-native';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';
import { useFonts } from 'expo-font';

import { theme } from './src/theme/theme';
import { Header } from './src/components/Header';
import { ImageUploader } from './src/components/ImageUploader';
import { StatusCard } from './src/components/StatusCard';
import { AttendanceList } from './src/components/AttendanceList';
import { ServerConfigModal } from './src/components/ServerConfigModal';
import { checkBackendHealth, recognizeFaceApi, fetchAttendanceRecords } from './src/api/attendanceApi';

export default function App() {
  const [fontsLoaded] = useFonts({
    ...Ionicons.font,
  });

  const [activeTab, setActiveTab] = useState('scan'); // 'scan' | 'logs'
  const [isOnline, setIsOnline] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [recognitionResult, setRecognitionResult] = useState(null);
  const [attendanceRecords, setAttendanceRecords] = useState([]);
  const [isRefreshingLogs, setIsRefreshingLogs] = useState(false);
  const [configModalVisible, setConfigModalVisible] = useState(false);

  // Check health and load attendance history on startup
  const checkHealthAndLoadData = useCallback(async () => {
    try {
      const health = await checkBackendHealth();
      setIsOnline(Boolean(health && health.success));

      const attendanceRes = await fetchAttendanceRecords();
      if (attendanceRes && attendanceRes.success && Array.isArray(attendanceRes.records)) {
        setAttendanceRecords(attendanceRes.records);
      }
    } catch (e) {
      console.error("Health & Data loading error:", e);
      setIsOnline(false);
    }
  }, []);

  useEffect(() => {
    checkHealthAndLoadData();

    const interval = setInterval(async () => {
      try {
        const health = await checkBackendHealth();
        setIsOnline(Boolean(health && health.success));
      } catch (e) {
        setIsOnline(false);
      }
    }, 10000);

    return () => clearInterval(interval);
  }, [checkHealthAndLoadData]);

  // Handle Face Recognition API Call
  const handleRecognizeFace = async () => {
    if (!selectedImage) {
      Alert.alert('No Image Selected', 'Please select an employee face image first.');
      return;
    }

    setIsAnalyzing(true);
    setRecognitionResult(null);

    try {
      const res = await recognizeFaceApi(selectedImage);

      if (res && res.success && res.data) {
        setRecognitionResult(res.data);
        
        if (res.data.recognized) {
          const updatedLogs = await fetchAttendanceRecords();
          if (updatedLogs && updatedLogs.success && Array.isArray(updatedLogs.records)) {
            setAttendanceRecords(updatedLogs.records);
          }
        }
      } else {
        setRecognitionResult({
          recognized: false,
          person: null,
          similarity: null,
          message: (res && res.message) || 'Error communicating with backend server.',
        });
      }
    } catch (error) {
      console.error('App recognition error:', error);
      setRecognitionResult({
        recognized: false,
        person: null,
        similarity: null,
        message: 'An unexpected error occurred during recognition.',
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Handle Pull-to-refresh on Logs tab
  const handleRefreshLogs = async () => {
    setIsRefreshingLogs(true);
    try {
      const health = await checkBackendHealth();
      setIsOnline(Boolean(health && health.success));
      const res = await fetchAttendanceRecords();
      if (res && res.success && Array.isArray(res.records)) {
        setAttendanceRecords(res.records);
      }
    } catch (e) {
      console.error("Refresh logs error:", e);
    } finally {
      setIsRefreshingLogs(false);
    }
  };

  if (!fontsLoaded) {
    return (
      <View style={styles.fontLoadingContainer}>
        <ActivityIndicator size="large" color={theme.colors.primary} />
        <Text style={styles.fontLoadingText}>Loading Face Attendance App...</Text>
      </View>
    );
  }

  return (
    <SafeAreaProvider>
      <SafeAreaView style={styles.safeArea}>
        <StatusBar style="dark" backgroundColor={theme.colors.white} />

        {/* Top App Header */}
        <Header 
          isOnline={isOnline} 
          onOpenConfig={() => setConfigModalVisible(true)} 
        />

        {/* Navigation Segment Tabs */}
        <View style={styles.tabContainer}>
          <TouchableOpacity
            style={[styles.tabButton, activeTab === 'scan' && styles.activeTabButton, styles.leftTabMargin]}
            onPress={() => setActiveTab('scan')}
            activeOpacity={0.8}
          >
            <Ionicons 
              name={activeTab === 'scan' ? "scan" : "scan-outline"} 
              size={18} 
              color={activeTab === 'scan' ? theme.colors.primary : theme.colors.textMuted} 
              style={styles.tabIconMargin}
            />
            <Text style={[styles.tabText, activeTab === 'scan' && styles.activeTabText]}>
              Mark Attendance
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.tabButton, activeTab === 'logs' && styles.activeTabButton]}
            onPress={() => setActiveTab('logs')}
            activeOpacity={0.8}
          >
            <Ionicons 
              name={activeTab === 'logs' ? "people" : "people-outline"} 
              size={18} 
              color={activeTab === 'logs' ? theme.colors.primary : theme.colors.textMuted} 
              style={styles.tabIconMargin}
            />
            <Text style={[styles.tabText, activeTab === 'logs' && styles.activeTabText]}>
              Employee Logs ({attendanceRecords.length})
            </Text>
          </TouchableOpacity>
        </View>

        {/* Main Screen Content */}
        {activeTab === 'scan' ? (
          <ScrollView 
            style={styles.scrollContent} 
            contentContainerStyle={styles.scrollBody}
            showsVerticalScrollIndicator={false}
          >
            {/* Offline Banner Warning */}
            {!isOnline && (
              <View style={styles.offlineBanner}>
                <Ionicons name="wifi-outline" size={18} color={theme.colors.warning} style={styles.bannerIconMargin} />
                <View style={styles.offlineBannerTextCol}>
                  <Text style={styles.offlineTitle}>Backend Disconnected</Text>
                  <Text style={styles.offlineSubtext}>
                    Ensure FastAPI backend is running at port 8000 or tap Settings to configure host IP.
                  </Text>
                </View>
              </View>
            )}

            {/* Image Picker Component */}
            <ImageUploader
              selectedImage={selectedImage}
              setSelectedImage={setSelectedImage}
              onRecognize={handleRecognizeFace}
              isLoading={isAnalyzing}
            />

            {/* Recognition Result Feedback Card */}
            <StatusCard result={recognitionResult} />
          </ScrollView>
        ) : (
          <View style={styles.logsView}>
            <AttendanceList 
              records={attendanceRecords} 
              onRefresh={handleRefreshLogs} 
              refreshing={isRefreshingLogs}
            />
          </View>
        )}

        {/* Server Endpoint Config Modal */}
        <ServerConfigModal
          visible={configModalVisible}
          onClose={() => setConfigModalVisible(false)}
          onSaved={checkHealthAndLoadData}
        />
      </SafeAreaView>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  fontLoadingContainer: {
    flex: 1,
    backgroundColor: theme.colors.background,
    alignItems: 'center',
    justifyContent: 'center',
  },
  fontLoadingText: {
    marginTop: 12,
    fontSize: 14,
    color: theme.colors.textSecondary,
    fontWeight: '500',
  },
  safeArea: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  tabContainer: {
    flexDirection: 'row',
    backgroundColor: theme.colors.white,
    marginHorizontal: theme.spacing.md,
    marginTop: theme.spacing.md,
    marginBottom: theme.spacing.xs,
    borderRadius: theme.borderRadius.md,
    padding: 4,
    borderWidth: 1,
    borderColor: theme.colors.cardBorder,
    ...theme.shadows.card,
  },
  tabButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 10,
    borderRadius: theme.borderRadius.sm,
  },
  leftTabMargin: {
    marginRight: 4,
  },
  tabIconMargin: {
    marginRight: 6,
  },
  activeTabButton: {
    backgroundColor: theme.colors.primaryLight,
    borderWidth: 1,
    borderColor: 'rgba(37, 99, 235, 0.25)',
  },
  tabText: {
    fontSize: 13,
    fontWeight: '600',
    color: theme.colors.textMuted,
  },
  activeTabText: {
    color: theme.colors.primary,
    fontWeight: '700',
  },
  scrollContent: {
    flex: 1,
  },
  scrollBody: {
    paddingBottom: theme.spacing.xl,
  },
  logsView: {
    flex: 1,
    marginTop: theme.spacing.sm,
  },
  offlineBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.colors.warningBg,
    borderWidth: 1,
    borderColor: theme.colors.warningBorder,
    borderRadius: theme.borderRadius.md,
    marginHorizontal: theme.spacing.md,
    marginTop: theme.spacing.sm,
    padding: theme.spacing.sm + 2,
  },
  bannerIconMargin: {
    marginRight: 10,
  },
  offlineBannerTextCol: {
    flex: 1,
  },
  offlineTitle: {
    fontSize: 13,
    fontWeight: '700',
    color: theme.colors.warning,
  },
  offlineSubtext: {
    fontSize: 11,
    color: theme.colors.textSecondary,
    marginTop: 2,
  },
});
