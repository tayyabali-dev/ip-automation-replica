import api from '@/lib/axios';
import { ApplicationHistoryItem } from '@/lib/types';

export interface GetApplicationsParams {
  skip?: number;
  limit?: number;
}

export const applicationsApi = {
  // Get list of applications for current user
  getApplications: async (params: GetApplicationsParams = {}) => {
    const { skip = 0, limit = 20 } = params;
    const response = await api.get<ApplicationHistoryItem[]>('/enhanced-applications', {
      params: { skip, limit }
    });
    return response.data;
  },

  // Get specific application by ID
  getApplication: async (applicationId: string) => {
    const response = await api.get<ApplicationHistoryItem>(`/enhanced-applications/${applicationId}`);
    return response.data;
  },

  // Generate ADS for an application (live extraction result)
  generateADS: async (applicationData: ApplicationHistoryItem) => {
    const response = await api.post('/generate-enhanced-ads', applicationData, {
      responseType: 'blob'
    });
    return response.data;
  },

  // Generate ADS from saved application
  generateADSFromSaved: async (applicationId: string) => {
    const response = await api.post(`/enhanced-applications/${applicationId}/generate-ads`, {}, {
      responseType: 'blob'
    });
    return response.data;
  }
};