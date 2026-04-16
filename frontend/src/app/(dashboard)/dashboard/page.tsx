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
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
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
          <p className="text-neutral-500 text-sm mb-1 flex items-center gap-1.5">
            <Star className="w-3 h-3 text-primary-500/50" />
            {formatDate()} — Metropolis Time
          </p>
          <h1 className="text-2xl md:text-3xl font-semibold tracking-tight text-neutral-100">
            {getGreeting()}, <span className="text-primary-500 text-glow-super">{user?.full_name?.split(' ')[0] || 'Hero'}</span>
          </h1>
        </div>
        <Link href="/dashboard/history">
          <Button variant="outline" size="sm" className="gap-2 border-primary-500/30 text-primary-400 hover:bg-primary-500/10 hover:border-primary-500/50">
            <ScrollText className="w-4 h-4" />
            Archives
          </Button>
        </Link>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white/90 dark:bg-[#0f172a]/90 backdrop-blur-sm border border-primary-500/20 rounded-xl p-4 hover:border-primary-500/40 transition-all">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-primary-500/10 border border-primary-500/30 flex items-center justify-center">
              <FileText className="w-5 h-5 text-primary-500 drop-shadow-[0_0_8px_rgba(253,185,19,0.5)]" />
            </div>
            <div>
              <p className="text-2xl font-semibold text-neutral-900 dark:text-neutral-100">{recentApplications.length}</p>
              <p className="text-xs text-neutral-600 dark:text-neutral-400">Active Missions</p>
            </div>
          </div>
        </div>

        <div className="bg-[#1a1a1a]/90 backdrop-blur-sm border border-primary-500/20 rounded-xl p-4 hover:border-primary-500/40 transition-all">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-batman-steel/10 border border-batman-steel/30 flex items-center justify-center">
              <Radar className="w-5 h-5 text-batman-steel drop-shadow-[0_0_6px_rgba(90,108,125,0.5)]" />
            </div>
            <div>
              <p className="text-2xl font-semibold text-neutral-900 dark:text-neutral-100">{recentOfficeActions.length}</p>
              <p className="text-xs text-neutral-600 dark:text-neutral-400">Threat Scans</p>
            </div>
          </div>
        </div>

        <div className="bg-[#1a1a1a]/90 backdrop-blur-sm border border-primary-500/20 rounded-xl p-4 hover:border-primary-500/40 transition-all">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-green-500/10 border border-green-500/30 flex items-center justify-center">
              <Shield className="w-5 h-5 text-green-400 drop-shadow-[0_0_6px_rgba(34,197,94,0.5)]" />
            </div>
            <div>
              <p className="text-2xl font-semibold text-neutral-900 dark:text-neutral-100">{totalItems}</p>
              <p className="text-xs text-neutral-600 dark:text-neutral-400">Missions Complete</p>
            </div>
          </div>
        </div>

        <div className="bg-[#1a1a1a]/90 backdrop-blur-sm border border-primary-500/20 rounded-xl p-4 hover:border-primary-500/40 transition-all">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-red-500/10 border border-red-500/30 flex items-center justify-center">
              <Crosshair className="w-5 h-5 text-red-400 drop-shadow-[0_0_6px_rgba(239,68,68,0.5)]" />
            </div>
            <div>
              <p className="text-2xl font-semibold text-neutral-900 dark:text-neutral-100">{totalRejections}</p>
              <p className="text-xs text-neutral-600 dark:text-neutral-400">Threats Detected</p>
            </div>
          </div>
        </div>
      </div>

      {/* Feature Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* ADS Generator */}
        <div className="bg-white/90 dark:bg-[#0f172a]/90 backdrop-blur-sm border border-primary-500/25 rounded-xl overflow-hidden group hover:border-primary-500/50 transition-all duration-300">
          <div className="flex">
            {/* Left accent bar */}
            <div className="w-1 bg-primary-500 shadow-[0_0_12px_rgba(253,185,19,0.6)]" />
            <div className="p-5 flex-1">
              <div className="flex items-start gap-4">
                <div className="w-11 h-11 rounded-xl bg-primary-500/15 border border-primary-500/40 flex items-center justify-center flex-shrink-0">
                  <Swords className="w-5 h-5 text-primary-500 drop-shadow-[0_0_10px_rgba(253,185,19,0.7)]" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-neutral-900 dark:text-neutral-100 mb-1">Patent Application System</h3>
                  <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-4 leading-relaxed">
                    Upload patent documents. Our super-powered AI will generate compliant application forms.
                  </p>
                  <Button asChild variant="primary" size="sm" className="bg-primary-500 hover:bg-primary-600 text-white font-bold shadow-[0_0_20px_rgba(206,17,38,0.4)] hover:shadow-[0_0_30px_rgba(206,17,38,0.6)] transition-all">
                    <Link href="/dashboard/new-application">
                      Start Mission
                      <ArrowRight className="w-3.5 h-3.5 ml-1.5 group-hover:translate-x-0.5 transition-transform" />
                    </Link>
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Office Action Analyzer */}
        <div className="bg-white/90 dark:bg-[#0f172a]/90 backdrop-blur-sm border border-metropolis/20 rounded-xl overflow-hidden group hover:border-metropolis/40 transition-all duration-300">
          <div className="flex">
            {/* Left accent bar */}
            <div className="w-1 bg-metropolis shadow-[0_0_10px_rgba(4,118,242,0.5)]" />
            <div className="p-5 flex-1">
              <div className="flex items-start gap-4">
                <div className="w-11 h-11 rounded-xl bg-metropolis/15 border border-metropolis/30 flex items-center justify-center flex-shrink-0">
                  <Radar className="w-5 h-5 text-metropolis drop-shadow-[0_0_8px_rgba(4,118,242,0.6)]" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-neutral-900 dark:text-neutral-100 mb-1">Threat Analysis</h3>
                  <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-4 leading-relaxed">
                    Analyze office actions for rejections, deadlines, and prior art. Generate heroic response strategy.
                  </p>
                  <Button asChild variant="outline" size="sm" className="border-metropolis/40 text-metropolis hover:bg-metropolis/10 hover:border-metropolis/60 group-hover:shadow-[0_0_15px_rgba(4,118,242,0.3)] transition-all">
                    <Link href="/dashboard/office-action">
                      Analyze Threat
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
        <div className="bg-white/90 dark:bg-[#0f172a]/90 backdrop-blur-sm border border-primary-500/20 rounded-xl">
          <div className="px-5 py-4 border-b border-primary-500/20">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-medium flex items-center gap-2 text-neutral-900 dark:text-neutral-100">
                <div className="w-6 h-6 rounded-md bg-primary-500/15 flex items-center justify-center">
                  <Swords className="w-3.5 h-3.5 text-primary-500" />
                </div>
                Recent Missions
              </h3>
              {recentApplications.length > 0 && (
                <Link href="/dashboard/history" className="text-xs text-primary-500 hover:text-primary-400 font-medium hover:underline">
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
                  <Swords className="w-6 h-6 text-neutral-500" />
                </div>
                <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-1">No missions yet</p>
                <p className="text-xs text-neutral-500 dark:text-neutral-600">Begin your first mission</p>
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
                      <p className="text-sm font-medium text-neutral-800 dark:text-neutral-200 truncate group-hover:text-primary-500 transition-colors">
                        {app.title || 'Untitled Mission'}
                      </p>
                      <p className="text-xs text-neutral-500 mt-0.5">
                        {app.application_number || 'Draft'} · {formatRelativeDate(app.created_at)}
                      </p>
                    </div>
                    <ArrowRight className="w-4 h-4 text-neutral-600 group-hover:text-primary-500 group-hover:translate-x-0.5 transition-all flex-shrink-0 ml-3" />
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Recent Office Actions */}
        <div className="bg-[#1a1a1a]/90 backdrop-blur-sm border border-primary-500/20 rounded-xl">
          <div className="px-5 py-4 border-b border-primary-500/20">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-medium flex items-center gap-2 text-neutral-100">
                <div className="w-6 h-6 rounded-md bg-red-500/15 flex items-center justify-center">
                  <Radar className="w-3.5 h-3.5 text-red-400" />
                </div>
                Recent Threat Scans
              </h3>
              {recentOfficeActions.length > 0 && (
                <Link href="/dashboard/history" className="text-xs text-primary-500 hover:text-primary-400 font-medium hover:underline">
                  View all
                </Link>
              )}
            </div>
          </div>
          <div className="p-5">
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <div className="w-5 h-5 border-2 border-red-500/20 border-t-red-500 rounded-full animate-spin" />
              </div>
            ) : recentOfficeActions.length === 0 ? (
              <div className="text-center py-8">
                <div className="w-12 h-12 rounded-full bg-red-500/10 border border-red-500/20 flex items-center justify-center mx-auto mb-3">
                  <Radar className="w-6 h-6 text-neutral-500" />
                </div>
                <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-1">No threat scans yet</p>
                <p className="text-xs text-neutral-500 dark:text-neutral-600">Start analyzing threats</p>
              </div>
            ) : (
              <div className="space-y-1">
                {recentOfficeActions.map((oa) => (
                  <Link
                    key={oa._id}
                    href={`/dashboard/office-action/${oa._id}/analysis`}
                    className="flex items-center justify-between p-3 -mx-3 rounded-lg hover:bg-red-500/5 transition-colors group"
                  >
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium text-neutral-200 truncate group-hover:text-red-400 transition-colors">
                        {oa.application_number || oa.title_of_invention || 'Investigation'}
                      </p>
                      <div className="flex items-center gap-2 mt-0.5">
                        <p className="text-xs text-neutral-500">
                          {oa.office_action_type || 'Analysis'} · {formatRelativeDate(oa.created_at || '')}
                        </p>
                        {oa.total_rejections > 0 && (
                          <span className="inline-flex items-center text-[10px] font-medium text-red-400 bg-red-500/10 border border-red-500/30 px-1.5 py-0.5 rounded">
                            {oa.total_rejections} threat{oa.total_rejections !== 1 ? 's' : ''}
                          </span>
                        )}
                      </div>
                    </div>
                    <ArrowRight className="w-4 h-4 text-neutral-600 group-hover:text-red-400 group-hover:translate-x-0.5 transition-all flex-shrink-0 ml-3" />
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Getting Started (only shown when no activity) */}
      {totalItems === 0 && !loading && (
        <div className="border-dashed border-2 border-primary-500/30 bg-primary-500/5 rounded-xl">
          <div className="p-8 text-center">
            <div className="w-14 h-14 rounded-full bg-primary-500/10 border border-primary-500/30 flex items-center justify-center mx-auto mb-4">
              <Sparkles className="w-7 h-7 text-primary-500 drop-shadow-[0_0_15px_rgba(253,185,19,0.6)]" />
            </div>
            <h3 className="font-semibold text-neutral-900 dark:text-neutral-100 mb-1">Metropolis Needs You</h3>
            <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-5 max-w-sm mx-auto">
              Truth and justice await. Choose your first mission to protect innovation in Metropolis.
            </p>
            <div className="flex items-center justify-center gap-3">
              <Button asChild variant="primary" size="sm" className="bg-primary-500 hover:bg-primary-600 text-white font-bold shadow-[0_0_15px_rgba(206,17,38,0.4)]">
                <Link href="/dashboard/new-application">
                  <Swords className="w-4 h-4 mr-1.5" />
                  New Mission
                </Link>
              </Button>
              <Button asChild variant="outline" size="sm" className="border-metropolis/40 text-metropolis hover:bg-metropolis/10">
                <Link href="/dashboard/office-action">
                  <Radar className="w-4 h-4 mr-1.5" />
                  Analyze Threat
                </Link>
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
