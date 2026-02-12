import api from '@/lib/axios';
import { OfficeActionHistoryItem, OfficeActionData } from '@/lib/types';

export interface GetOfficeActionsParams {
  skip?: number;
  limit?: number;
}

export const officeActionsApi = {
  // Get list of office actions for current user
  getOfficeActions: async (params: GetOfficeActionsParams = {}) => {
    const { skip = 0, limit = 20 } = params;
    const response = await api.get<OfficeActionHistoryItem[]>('/office-actions/history', {
      params: { skip, limit }
    });
    return response.data;
  },

  // Get specific office action by document ID
  getOfficeAction: async (documentId: string) => {
    const response = await api.get<OfficeActionData>(`/office-actions/${documentId}`);
    return response.data;
  },

  // Download report
  downloadReport: async (documentId: string) => {
    const response = await api.get(`/office-actions/${documentId}/report`, {
      responseType: 'blob'
    });
    return response.data;
  },

  // Download response shell
  downloadResponseShell: async (documentId: string, firmInfo?: {
    firm_name?: string;
    attorney_name?: string;
    attorney_reg_number?: string;
    firm_address?: string;
    firm_phone?: string;
    firm_email?: string;
  }) => {
    const response = await api.get(`/office-actions/${documentId}/response-shell`, {
      params: firmInfo,
      responseType: 'blob'
    });
    return response.data;
  }
};
