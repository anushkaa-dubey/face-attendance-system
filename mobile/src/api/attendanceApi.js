import { API_ENDPOINTS } from './config';
import { Platform } from 'react-native';

/**
 * Check if backend server is online
 */
export const checkBackendHealth = async () => {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 4000);
    
    const response = await fetch(API_ENDPOINTS.HEALTH(), {
      method: 'GET',
      signal: controller.signal,
    });
    clearTimeout(timeoutId);

    if (response.ok) {
      const data = await response.json();
      return { success: true, data };
    }
    return { success: false, error: `Server returned status ${response.status}` };
  } catch (error) {
    return { success: false, error: 'Cannot connect to backend server. Make sure FastAPI is running on port 8000.' };
  }
};

/**
 * Upload image to /recognize endpoint
 * @param {Object} imageResult - Image object from expo-image-picker
 */
export const recognizeFaceApi = async (imageResult) => {
  try {
    const formData = new FormData();

    if (Platform.OS === 'web') {
      // Handle web platform blob/file conversion
      const response = await fetch(imageResult.uri);
      const blob = await response.blob();
      const filename = imageResult.fileName || `face_${Date.now()}.jpg`;
      const file = new File([blob], filename, { type: blob.type || 'image/jpeg' });
      formData.append('file', file);
    } else {
      // Handle React Native iOS/Android
      const uri = imageResult.uri;
      const fileType = imageResult.mimeType || 'image/jpeg';
      const fileName = imageResult.fileName || `face_${Date.now()}.jpg`;

      formData.append('file', {
        uri: Platform.OS === 'android' ? uri : uri.replace('file://', ''),
        name: fileName,
        type: fileType,
      });
    }

    const response = await fetch(API_ENDPOINTS.RECOGNIZE(), {
      method: 'POST',
      body: formData,
      headers: {
        'Accept': 'application/json',
        // Note: Do NOT manually set Content-Type header when sending FormData,
        // let fetch automatically add the boundary!
      },
    });

    const data = await response.json();

    if (!response.ok) {
      return {
        success: false,
        message: data.detail || `Server error (${response.status})`,
      };
    }

    return {
      success: true,
      data: data, // { recognized: bool, person: str, similarity: float, message: str }
    };
  } catch (error) {
    console.error('Recognition error:', error);
    return {
      success: false,
      message: 'Network error. Please check backend connection.',
      error: error.message,
    };
  }
};

/**
 * Fetch all attendance records from backend
 */
export const fetchAttendanceRecords = async () => {
  try {
    const response = await fetch(API_ENDPOINTS.ATTENDANCE(), {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });

    if (!response.ok) {
      return { success: false, records: [], error: `Error ${response.status}` };
    }

    const data = await response.json();
    return { success: true, records: data };
  } catch (error) {
    console.error('Fetch attendance error:', error);
    return { success: false, records: [], error: 'Failed to fetch attendance history.' };
  }
};
