import { Platform } from 'react-native';

// Default host based on environment
const getDefaultApiUrl = () => {
  // Web browser or standard localhost
  if (Platform.OS === 'web') {
    return 'http://localhost:8000';
  }
  // Android emulator accesses host machine at 10.0.2.2
  if (Platform.OS === 'android') {
    return 'http://10.0.2.2:8000';
  }
  // iOS Simulator / default
  return 'http://localhost:8000';
};

let currentApiUrl = getDefaultApiUrl();

export const getApiUrl = () => currentApiUrl;

export const setApiUrl = (url) => {
  let formatted = url.trim();
  if (formatted.endsWith('/')) {
    formatted = formatted.slice(0, -1);
  }
  if (!formatted.startsWith('http://') && !formatted.startsWith('https://')) {
    formatted = `http://${formatted}`;
  }
  currentApiUrl = formatted;
  return currentApiUrl;
};

export const API_ENDPOINTS = {
  HEALTH: () => `${getApiUrl()}/health`,
  RECOGNIZE: () => `${getApiUrl()}/recognize`,
  ATTENDANCE: () => `${getApiUrl()}/attendance`,
};
