'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import {
  Swords,
  ScrollText,
  ArrowRight,
  FileText,
  Radar,
  Shield,
  Crosshair,
  Zap,
  Sparkles,
  Star
} from 'lucide-react';
import { applicationsApi } from '@/lib/api/applications';
import { officeActionsApi } from '@/lib/api/officeActions';
import { ApplicationHistoryItem, OfficeActionHistoryItem } from '@/lib/types';

export default function DashboardPage() {
  const { user } = useAuth();
  const [recentApplications, setRecentApplications] = useState<ApplicationHistoryItem[]>([]);
  const [recentOfficeActions, setRecentOfficeActions] = useState<OfficeActionHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRecentItems();
  }, []);

  const loadRecentItems = async () => {
    try {
      const [apps, oas] = await Promise.all([
        applicationsApi.getApplications({ skip: 0, limit: 5 }),
        officeActionsApi.getOfficeActions({ skip: 0, limit: 5 })
      ]);
      setRecentApplications(apps);
      setRecentOfficeActions(oas);
    } catch (err) {
      console.error('Error loading recent items:', err);
    } finally {
      setLoading(false);
    }
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning, Trainer';
    if (hour < 18) return 'Good afternoon, Trainer';
    return 'Good evening, Trainer';
  };

  const formatDate = () => {
    return new Date().toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatRelativeDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const totalItems = recentApplications.length + recentOfficeActions.length;
  const totalRejections = recentOfficeActions.reduce((sum, oa) => sum + (oa.total_rejections || 0), 0);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <p className="text-neutral-500 dark:text-neutral-400 text-sm mb-1 flex items-center gap-1.5">
            <Star className="w-3 h-3 text-pokemon-yellow" />
            {formatDate()}
          </p>
          <h1 className="text-2xl md:text-3xl font-semibold tracking-tight text-neutral-900 dark:text-neutral-100">
            {getGreeting()}, <span className="text-primary-500 text-glow-red">{user?.full_name?.split(' ')[0] || 'Ash'}</span>
          </h1>
        </div>
        <Link href="/dashboard/history">
          <Button variant="outline" size="sm" className="gap-2 border-primary-500/20 text-primary-500 hover:bg-primary-500/10 hover:border-primary-500/30">
            <ScrollText className="w-4 h-4" />
            Patent Archives
          </Button>
        </Link>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white/90 dark:bg-[#1e293b]/90 backdrop-blur-sm border border-primary-500/15 rounded-xl p-4 hover:border-primary-500/30 transition-all">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-pokemon-water/10 border border-pokemon-water/30 flex items-center justify-center">
              <FileText className="w-5 h-5 text-pokemon-water drop-shadow-[0_0_6px_rgba(74,144,226,0.5)]" />
            </div>
            <div>
              <p className="text-2xl font-semibold text-neutral-900 dark:text-neutral-100">{recentApplications.length}</p>
              <p className="text-xs text-neutral-500 dark:text-neutral-400">Patents Filed</p>
            </div>
          </div>
        </div>

        <div className="bg-white/90 dark:bg-[#1e293b]/90 backdrop-blur-sm border border-primary-500/15 rounded-xl p-4 hover:border-primary-500/30 transition-all">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-pokemon-electric/10 border border-pokemon-electric/30 flex items-center justify-center">
              <Radar className="w-5 h-5 text-pokemon-electric drop-shadow-[0_0_6px_rgba(247,208,44,0.5)]" />
            </div>
            <div>
              <p className="text-2xl font-semibold text-neutral-900 dark:text-neutral-100">{recentOfficeActions.length}</p>
              <p className="text-xs text-neutral-500 dark:text-neutral-400">Office Actions</p>
            </div>
          </div>
        </div>

        <div className="bg-white/90 dark:bg-[#1e293b]/90 backdrop-blur-sm border border-primary-500/15 rounded-xl p-4 hover:border-primary-500/30 transition-all">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-pokemon-grass/10 border border-pokemon-grass/30 flex items-center justify-center">
              <Shield className="w-5 h-5 text-pokemon-grass drop-shadow-[0_0_6px_rgba(120,200,80,0.5)]" />
            </div>
            <div>
              <p className="text-2xl font-semibold text-neutral-900 dark:text-neutral-100">{totalItems}</p>
              <p className="text-xs text-neutral-500 dark:text-neutral-400">Total Caught</p>
            </div>
          </div>
        </div>

        <div className="bg-white/90 dark:bg-[#1e293b]/90 backdrop-blur-sm border border-primary-500/15 rounded-xl p-4 hover:border-primary-500/30 transition-all">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-pokemon-fire/10 border border-pokemon-fire/30 flex items-center justify-center">
              <Crosshair className="w-5 h-5 text-pokemon-fire drop-shadow-[0_0_6px_rgba(255,156,84,0.5)]" />
            </div>
            <div>
              <p className="text-2xl font-semibold text-neutral-900 dark:text-neutral-100">{totalRejections}</p>
              <p className="text-xs text-neutral-500 dark:text-neutral-400">Challenges</p>
            </div>
          </div>
        </div>
      </div>

      {/* Feature Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* ADS Generator */}
        <div className="bg-white/90 dark:bg-[#1e293b]/90 backdrop-blur-sm border border-pokemon-water/20 rounded-xl overflow-hidden group hover:border-pokemon-water/40 transition-all duration-300">
          <div className="flex">
            {/* Left accent bar */}
            <div className="w-1 bg-pokemon-water shadow-[0_0_8px_rgba(74,144,226,0.5)]" />
            <div className="p-5 flex-1">
              <div className="flex items-start gap-4">
                <div className="w-11 h-11 rounded-xl bg-pokemon-water/15 border border-pokemon-water/30 flex items-center justify-center flex-shrink-0">
                  <Swords className="w-5 h-5 text-pokemon-water drop-shadow-[0_0_8px_rgba(74,144,226,0.6)]" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-neutral-900 dark:text-neutral-100 mb-1">Patent Application</h3>
                  <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-4 leading-relaxed">
                    Upload your patent documents. Our AI will generate compliant application forms instantly.
                  </p>
                  <Button asChild variant="primary" size="sm" className="bg-pokemon-water hover:bg-pokemon-water/90 text-white font-bold shadow-[0_0_15px_rgba(74,144,226,0.3)] hover:shadow-[0_0_20px_rgba(74,144,226,0.5)] transition-all">
                    <Link href="/dashboard/new-application">
                      Start Application
                      <ArrowRight className="w-3.5 h-3.5 ml-1.5 group-hover:translate-x-0.5 transition-transform" />
                    </Link>
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Office Action Analyzer */}
        <div className="bg-white/90 dark:bg-[#1e293b]/90 backdrop-blur-sm border border-pokemon-fire/20 rounded-xl overflow-hidden group hover:border-pokemon-fire/40 transition-all duration-300">
          <div className="flex">
            {/* Left accent bar */}
            <div className="w-1 bg-pokemon-fire shadow-[0_0_8px_rgba(255,156,84,0.5)]" />
            <div className="p-5 flex-1">
              <div className="flex items-start gap-4">
                <div className="w-11 h-11 rounded-xl bg-pokemon-fire/15 border border-pokemon-fire/30 flex items-center justify-center flex-shrink-0">
                  <Radar className="w-5 h-5 text-pokemon-fire drop-shadow-[0_0_8px_rgba(255,156,84,0.6)]" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-neutral-900 dark:text-neutral-100 mb-1">Office Action Analyzer</h3>
                  <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-4 leading-relaxed">
                    Analyze office actions for rejections, deadlines, and prior art. Generate response templates.
                  </p>
                  <Button asChild variant="outline" size="sm" className="border-pokemon-fire/30 text-pokemon-fire hover:bg-pokemon-fire/10 hover:border-pokemon-fire/50 group-hover:shadow-[0_0_10px_rgba(255,156,84,0.2)] transition-all">
                    <Link href="/dashboard/office-action">
                      Analyze Action
                      <ArrowRight className="w-3.5 h-3.5 ml-1.5 group-hover:translate-x-0.5 transition-transform" />
                    </Link>
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Recent Applications */}
        <div className="bg-white/90 dark:bg-[#1e293b]/90 backdrop-blur-sm border border-primary-500/15 rounded-xl">
          <div className="px-5 py-4 border-b border-primary-500/15">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-medium flex items-center gap-2 text-neutral-900 dark:text-neutral-100">
                <div className="w-6 h-6 rounded-md bg-pokemon-water/15 flex items-center justify-center">
                  <Swords className="w-3.5 h-3.5 text-pokemon-water" />
                </div>
                Recent Applications
              </h3>
              {recentApplications.length > 0 && (
                <Link href="/dashboard/history" className="text-xs text-primary-500 hover:text-primary-600 font-medium hover:underline">
                  View all
                </Link>
              )}
            </div>
          </div>
          <div className="p-5">
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <div className="w-5 h-5 border-2 border-primary-500/20 border-t-primary-500 rounded-full animate-spin" />
              </div>
            ) : recentApplications.length === 0 ? (
              <div className="text-center py-8">
                <div className="w-12 h-12 rounded-full bg-primary-500/10 border border-primary-500/20 flex items-center justify-center mx-auto mb-3">
                  <Swords className="w-6 h-6 text-neutral-400" />
                </div>
                <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-1">No applications yet</p>
                <p className="text-xs text-neutral-500 dark:text-neutral-500">Start your first patent application</p>
              </div>
            ) : (
              <div className="space-y-1">
                {recentApplications.map((app) => (
                  <Link
                    key={app._id}
                    href={`/dashboard/history/${app._id}`}
                    className="flex items-center justify-between p-3 -mx-3 rounded-lg hover:bg-primary-500/5 transition-colors group"
                  >
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium text-neutral-800 dark:text-neutral-200 truncate group-hover:text-pokemon-water transition-colors">
                        {app.title || 'Untitled Application'}
                      </p>
                      <p className="text-xs text-neutral-500 dark:text-neutral-400 mt-0.5">
                        {app.application_number || 'Draft'} · {formatRelativeDate(app.created_at)}
                      </p>
                    </div>
                    <ArrowRight className="w-4 h-4 text-neutral-400 group-hover:text-pokemon-water group-hover:translate-x-0.5 transition-all flex-shrink-0 ml-3" />
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Recent Office Actions */}
        <div className="bg-white/90 dark:bg-[#1e293b]/90 backdrop-blur-sm border border-primary-500/15 rounded-xl">
          <div className="px-5 py-4 border-b border-primary-500/15">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-medium flex items-center gap-2 text-neutral-900 dark:text-neutral-100">
                <div className="w-6 h-6 rounded-md bg-pokemon-fire/15 flex items-center justify-center">
                  <Radar className="w-3.5 h-3.5 text-pokemon-fire" />
                </div>
                Recent Office Actions
              </h3>
              {recentOfficeActions.length > 0 && (
                <Link href="/dashboard/history" className="text-xs text-primary-500 hover:text-primary-600 font-medium hover:underline">
                  View all
                </Link>
              )}
            </div>
          </div>
          <div className="p-5">
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <div className="w-5 h-5 border-2 border-pokemon-fire/20 border-t-pokemon-fire rounded-full animate-spin" />
              </div>
            ) : recentOfficeActions.length === 0 ? (
              <div className="text-center py-8">
                <div className="w-12 h-12 rounded-full bg-pokemon-fire/10 border border-pokemon-fire/20 flex items-center justify-center mx-auto mb-3">
                  <Radar className="w-6 h-6 text-neutral-400" />
                </div>
                <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-1">No office actions yet</p>
                <p className="text-xs text-neutral-500 dark:text-neutral-500">Analyze your first office action</p>
              </div>
            ) : (
              <div className="space-y-1">
                {recentOfficeActions.map((oa) => (
                  <Link
                    key={oa._id}
                    href={`/dashboard/office-action/${oa._id}/analysis`}
                    className="flex items-center justify-between p-3 -mx-3 rounded-lg hover:bg-primary-500/5 transition-colors group"
                  >
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium text-neutral-800 dark:text-neutral-200 truncate group-hover:text-pokemon-fire transition-colors">
                        {oa.application_number || oa.title_of_invention || 'Office Action'}
                      </p>
                      <div className="flex items-center gap-2 mt-0.5">
                        <p className="text-xs text-neutral-500 dark:text-neutral-400">
                          {oa.office_action_type || 'Analysis'} · {formatRelativeDate(oa.created_at || '')}
                        </p>
                        {oa.total_rejections > 0 && (
                          <span className="inline-flex items-center text-[10px] font-medium text-pokemon-fire bg-pokemon-fire/10 border border-pokemon-fire/30 px-1.5 py-0.5 rounded">
                            {oa.total_rejections} rejection{oa.total_rejections !== 1 ? 's' : ''}
                          </span>
                        )}
                      </div>
                    </div>
                    <ArrowRight className="w-4 h-4 text-neutral-400 group-hover:text-pokemon-fire group-hover:translate-x-0.5 transition-all flex-shrink-0 ml-3" />
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Getting Started (only shown when no activity) */}
      {totalItems === 0 && !loading && (
        <div className="border-dashed border-2 border-primary-500/20 bg-primary-500/5 rounded-xl">
          <div className="p-8 text-center">
            <div className="w-14 h-14 rounded-full bg-pokemon-yellow/10 border border-pokemon-yellow/30 flex items-center justify-center mx-auto mb-4">
              <Sparkles className="w-7 h-7 text-pokemon-yellow drop-shadow-[0_0_10px_rgba(255,203,5,0.5)]" />
            </div>
            <h3 className="font-semibold text-neutral-900 dark:text-neutral-100 mb-1">Begin Your Journey</h3>
            <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-5 max-w-sm mx-auto">
              Ready to catch some patents? Choose your first adventure to get started.
            </p>
            <div className="flex items-center justify-center gap-3">
              <Button asChild variant="primary" size="sm" className="bg-pokemon-water hover:bg-pokemon-water/90 text-white font-bold">
                <Link href="/dashboard/new-application">
                  <Swords className="w-4 h-4 mr-1.5" />
                  New Patent
                </Link>
              </Button>
              <Button asChild variant="outline" size="sm" className="border-pokemon-fire/30 text-pokemon-fire hover:bg-pokemon-fire/10">
                <Link href="/dashboard/office-action">
                  <Radar className="w-4 h-4 mr-1.5" />
                  Analyze Action
                </Link>
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
