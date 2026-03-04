'use client';

import React, { useState, useEffect } from 'react';
import { notificationsApi, Notification, CreateNotificationRequest } from '@/lib/api/notifications';
import { Button } from '@/components/ui/button';
import { 
  Bell, 
  Trash2, 
  Check, 
  X, 
  AlertCircle, 
  CheckCircle, 
  Info, 
  AlertTriangle,
  Radio,
  Zap,
  Plus,
  RotateCcw
} from 'lucide-react';
import { useForm } from 'react-hook-form';

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [unreadCount, setUnreadCount] = useState(0);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [filterRead, setFilterRead] = useState<'all' | 'unread' | 'read'>('all');
  
  const { register, handleSubmit, reset, formState: { errors } } = useForm<CreateNotificationRequest>();

  useEffect(() => {
    loadNotifications();
    loadUnreadCount();
  }, [filterRead]);

  const loadNotifications = async () => {
    try {
      setLoading(true);
      const params = filterRead === 'all' ? {} : { is_read: filterRead === 'read' };
      const data = await notificationsApi.getNotifications(params);
      setNotifications(data);
    } catch (error) {
      console.error('Failed to load notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadUnreadCount = async () => {
    try {
      const { count } = await notificationsApi.getUnreadCount();
      setUnreadCount(count);
    } catch (error) {
      console.error('Failed to load unread count:', error);
    }
  };

  const handleCreateNotification = async (data: CreateNotificationRequest) => {
    try {
      await notificationsApi.createNotification(data);
      reset();
      setShowCreateForm(false);
      await loadNotifications();
      await loadUnreadCount();
    } catch (error) {
      console.error('Failed to create notification:', error);
    }
  };

  const handleMarkAsRead = async (id: string) => {
    try {
      await notificationsApi.markAsRead(id);
      await loadNotifications();
      await loadUnreadCount();
    } catch (error) {
      console.error('Failed to mark as read:', error);
    }
  };

  const handleMarkAsUnread = async (id: string) => {
    try {
      await notificationsApi.markAsUnread(id);
      await loadNotifications();
      await loadUnreadCount();
    } catch (error) {
      console.error('Failed to mark as unread:', error);
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await notificationsApi.markAllAsRead();
      await loadNotifications();
      await loadUnreadCount();
    } catch (error) {
      console.error('Failed to mark all as read:', error);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this transmission?')) return;
    
    try {
      await notificationsApi.deleteNotification(id);
      await loadNotifications();
      await loadUnreadCount();
    } catch (error) {
      console.error('Failed to delete notification:', error);
    }
  };

  const handleDeleteAll = async () => {
    if (!confirm('Delete all transmissions? This action cannot be undone.')) return;
    
    try {
      await notificationsApi.deleteAll();
      await loadNotifications();
      await loadUnreadCount();
    } catch (error) {
      console.error('Failed to delete all:', error);
    }
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'success':
        return <CheckCircle className="w-5 h-5 text-saber-green" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-saber-red" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-primary-500" />;
      case 'transmission':
        return <Radio className="w-5 h-5 text-saber-blue" />;
      default:
        return <Info className="w-5 h-5 text-neutral-400" />;
    }
  };

  const getNotificationColor = (type: string) => {
    switch (type) {
      case 'success':
        return 'border-saber-green/20 bg-saber-green/5';
      case 'error':
        return 'border-saber-red/20 bg-saber-red/5';
      case 'warning':
        return 'border-primary-500/20 bg-primary-500/5';
      case 'transmission':
        return 'border-saber-blue/20 bg-saber-blue/5';
      default:
        return 'border-primary-500/10 bg-[#0d0e14]/50';
    }
  };

  const getPriorityBadge = (priority: string) => {
    const colors = {
      urgent: 'bg-saber-red/20 text-saber-red border-saber-red/30',
      high: 'bg-primary-500/20 text-primary-500 border-primary-500/30',
      medium: 'bg-saber-blue/20 text-saber-blue border-saber-blue/30',
      low: 'bg-neutral-500/20 text-neutral-400 border-neutral-500/30',
    };
    
    return colors[priority as keyof typeof colors] || colors.medium;
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-semibold tracking-tight text-neutral-100 flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-primary-500/10 border border-primary-500/20 flex items-center justify-center">
              <Bell className="w-5 h-5 text-primary-500 drop-shadow-[0_0_8px_rgba(255,232,31,0.5)]" />
            </div>
            Holonet Transmissions
          </h1>
          <p className="text-neutral-400 text-sm mt-1">
            {unreadCount > 0 ? (
              <span className="text-primary-500">{unreadCount} unread transmission{unreadCount !== 1 ? 's' : ''}</span>
            ) : (
              'All transmissions read'
            )}
          </p>
        </div>
        
        <div className="flex items-center gap-2">
          <Button
            onClick={() => setShowCreateForm(!showCreateForm)}
            variant="primary"
            size="sm"
            className="bg-saber-blue hover:bg-saber-blue/80 text-black font-bold shadow-[0_0_15px_rgba(79,195,247,0.3)]"
          >
            <Plus className="w-4 h-4 mr-1.5" />
            New Transmission
          </Button>
        </div>
      </div>

      {/* Create Form */}
      {showCreateForm && (
        <div className="bg-[#0d0e14]/80 backdrop-blur-sm border border-saber-blue/20 rounded-xl p-6 shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-neutral-100 flex items-center gap-2">
              <Zap className="w-4 h-4 text-saber-blue" />
              Compose Transmission
            </h3>
            <button
              onClick={() => setShowCreateForm(false)}
              className="p-1 rounded-lg hover:bg-white/10 text-neutral-400 hover:text-neutral-200 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          <form onSubmit={handleSubmit(handleCreateNotification)} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-primary-500/70 uppercase tracking-wider mb-1.5">
                Title
              </label>
              <input
                type="text"
                {...register('title', { required: 'Title is required' })}
                className="w-full rounded-lg border border-primary-500/15 bg-black/40 px-3 py-2 text-sm text-white placeholder:text-neutral-600 focus:border-primary-500/50 focus:ring-1 focus:ring-primary-500/20 focus:outline-none transition-all"
                placeholder="Incoming transmission from..."
              />
              {errors.title && <p className="text-xs text-red-400 mt-1">{errors.title.message}</p>}
            </div>

            <div>
              <label className="block text-xs font-medium text-primary-500/70 uppercase tracking-wider mb-1.5">
                Message
              </label>
              <textarea
                {...register('message', { required: 'Message is required' })}
                rows={3}
                className="w-full rounded-lg border border-primary-500/15 bg-black/40 px-3 py-2 text-sm text-white placeholder:text-neutral-600 focus:border-primary-500/50 focus:ring-1 focus:ring-primary-500/20 focus:outline-none transition-all resize-none"
                placeholder="Transmission content..."
              />
              {errors.message && <p className="text-xs text-red-400 mt-1">{errors.message.message}</p>}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-primary-500/70 uppercase tracking-wider mb-1.5">
                  Type
                </label>
                <select
                  {...register('notification_type')}
                  className="w-full rounded-lg border border-primary-500/15 bg-black/40 px-3 py-2 text-sm text-white focus:border-primary-500/50 focus:ring-1 focus:ring-primary-500/20 focus:outline-none transition-all"
                >
                  <option value="info">Info</option>
                  <option value="success">Success</option>
                  <option value="warning">Warning</option>
                  <option value="error">Error</option>
                  <option value="transmission">Transmission</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-primary-500/70 uppercase tracking-wider mb-1.5">
                  Priority
                </label>
                <select
                  {...register('priority')}
                  className="w-full rounded-lg border border-primary-500/15 bg-black/40 px-3 py-2 text-sm text-white focus:border-primary-500/50 focus:ring-1 focus:ring-primary-500/20 focus:outline-none transition-all"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="urgent">Urgent</option>
                </select>
              </div>
            </div>

            <div className="flex items-center gap-2 pt-2">
              <Button type="submit" variant="primary" size="sm" className="bg-saber-blue hover:bg-saber-blue/80 text-black font-bold">
                <Zap className="w-3.5 h-3.5 mr-1.5" />
                Send Transmission
              </Button>
              <Button
                type="button"
                onClick={() => setShowCreateForm(false)}
                variant="outline"
                size="sm"
                className="border-neutral-700 text-neutral-400"
              >
                Cancel
              </Button>
            </div>
          </form>
        </div>
      )}

      {/* Filter Tabs */}
      <div className="flex items-center gap-2">
        <button
          onClick={() => setFilterRead('all')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
            filterRead === 'all'
              ? 'bg-primary-500/20 text-primary-500 border border-primary-500/30'
              : 'bg-white/5 text-neutral-400 hover:bg-white/10 border border-transparent'
          }`}
        >
          All
        </button>
        <button
          onClick={() => setFilterRead('unread')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
            filterRead === 'unread'
              ? 'bg-primary-500/20 text-primary-500 border border-primary-500/30'
              : 'bg-white/5 text-neutral-400 hover:bg-white/10 border border-transparent'
          }`}
        >
          Unread {unreadCount > 0 && <span className="ml-1.5 text-xs">({unreadCount})</span>}
        </button>
        <button
          onClick={() => setFilterRead('read')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
            filterRead === 'read'
              ? 'bg-primary-500/20 text-primary-500 border border-primary-500/30'
              : 'bg-white/5 text-neutral-400 hover:bg-white/10 border border-transparent'
          }`}
        >
          Read
        </button>
        
        <div className="flex-1" />
        
        {unreadCount > 0 && (
          <Button
            onClick={handleMarkAllAsRead}
            variant="ghost"
            size="sm"
            className="text-neutral-400 hover:text-neutral-200"
          >
            <Check className="w-4 h-4 mr-1.5" />
            Mark all read
          </Button>
        )}
        
        {notifications.length > 0 && (
          <Button
            onClick={handleDeleteAll}
            variant="ghost"
            size="sm"
            className="text-neutral-400 hover:text-red-400"
          >
            <Trash2 className="w-4 h-4 mr-1.5" />
            Delete all
          </Button>
        )}

        <Button
          onClick={loadNotifications}
          variant="ghost"
          size="sm"
          className="text-neutral-400 hover:text-primary-500"
        >
          <RotateCcw className="w-4 h-4" />
        </Button>
      </div>

      {/* Notifications List */}
      <div className="space-y-3">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="w-6 h-6 border-2 border-primary-500/20 border-t-primary-500 rounded-full animate-spin" />
          </div>
        ) : notifications.length === 0 ? (
          <div className="text-center py-12 bg-[#0d0e14]/50 border border-primary-500/10 rounded-xl">
            <div className="w-14 h-14 rounded-full bg-primary-500/10 border border-primary-500/20 flex items-center justify-center mx-auto mb-4">
              <Bell className="w-7 h-7 text-neutral-600" />
            </div>
            <p className="text-neutral-400 mb-1">No transmissions found</p>
            <p className="text-xs text-neutral-600">
              {filterRead === 'unread' ? 'All transmissions have been acknowledged' : 'Your holonet is silent'}
            </p>
          </div>
        ) : (
          notifications.map((notification) => (
            <div
              key={notification._id}
              className={`p-4 rounded-xl border backdrop-blur-sm transition-all hover:border-primary-500/30 ${
                getNotificationColor(notification.notification_type)
              } ${!notification.is_read ? 'shadow-lg' : 'opacity-70'}`}
            >
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0 mt-0.5">
                  {getNotificationIcon(notification.notification_type)}
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2 mb-1">
                    <h4 className={`text-sm font-semibold ${!notification.is_read ? 'text-neutral-100' : 'text-neutral-300'}`}>
                      {notification.title}
                    </h4>
                    <div className="flex items-center gap-1.5">
                      <span className={`text-[10px] px-2 py-0.5 rounded border font-medium uppercase tracking-wider ${getPriorityBadge(notification.priority)}`}>
                        {notification.priority}
                      </span>
                    </div>
                  </div>
                  
                  <p className="text-sm text-neutral-400 mb-2 leading-relaxed">
                    {notification.message}
                  </p>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-neutral-500">
                      {formatDate(notification.created_at)}
                    </span>
                    
                    <div className="flex items-center gap-1">
                      {notification.is_read ? (
                        <button
                          onClick={() => handleMarkAsUnread(notification._id)}
                          className="p-1.5 rounded-lg hover:bg-white/10 text-neutral-500 hover:text-primary-500 transition-colors"
                          title="Mark as unread"
                        >
                          <RotateCcw className="w-3.5 h-3.5" />
                        </button>
                      ) : (
                        <button
                          onClick={() => handleMarkAsRead(notification._id)}
                          className="p-1.5 rounded-lg hover:bg-saber-green/20 text-neutral-500 hover:text-saber-green transition-colors"
                          title="Mark as read"
                        >
                          <Check className="w-3.5 h-3.5" />
                        </button>
                      )}
                      
                      <button
                        onClick={() => handleDelete(notification._id)}
                        className="p-1.5 rounded-lg hover:bg-red-500/20 text-neutral-500 hover:text-red-400 transition-colors"
                        title="Delete"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
