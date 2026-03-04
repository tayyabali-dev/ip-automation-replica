import api from '../axios';

export interface Notification {
  _id: string;
  title: string;
  message: string;
  notification_type: 'info' | 'warning' | 'success' | 'error' | 'transmission';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  user_id: string;
  is_read: boolean;
  created_at: string;
  read_at?: string;
}

export interface CreateNotificationRequest {
  title: string;
  message: string;
  notification_type?: 'info' | 'warning' | 'success' | 'error' | 'transmission';
  priority?: 'low' | 'medium' | 'high' | 'urgent';
}

export const notificationsApi = {
  // Get all notifications
  getNotifications: async (params?: { skip?: number; limit?: number; is_read?: boolean }): Promise<Notification[]> => {
    const response = await api.get('/notifications/', { params });
    return response.data;
  },

  // Get unread count
  getUnreadCount: async (): Promise<{ count: number }> => {
    const response = await api.get('/notifications/unread-count');
    return response.data;
  },

  // Create a notification
  createNotification: async (data: CreateNotificationRequest): Promise<Notification> => {
    const response = await api.post('/notifications/', data);
    return response.data;
  },

  // Mark notification as read
  markAsRead: async (id: string): Promise<Notification> => {
    const response = await api.put(`/notifications/${id}`, { is_read: true });
    return response.data;
  },

  // Mark notification as unread
  markAsUnread: async (id: string): Promise<Notification> => {
    const response = await api.put(`/notifications/${id}`, { is_read: false });
    return response.data;
  },

  // Mark all as read
  markAllAsRead: async (): Promise<{ updated: number }> => {
    const response = await api.post('/notifications/mark-all-read');
    return response.data;
  },

  // Delete a notification
  deleteNotification: async (id: string): Promise<void> => {
    await api.delete(`/notifications/${id}`);
  },

  // Delete all notifications
  deleteAll: async (): Promise<void> => {
    await api.delete('/notifications/');
  },
};
