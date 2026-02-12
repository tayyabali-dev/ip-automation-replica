'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import {
  FilePlus,
  Clock,
  ArrowRight,
  FileText,
  FileSearch,
  CheckCircle2,
  BarChart3,
  Sparkles
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
          <p className="text-neutral-500 text-sm mb-1">
            {formatDate()}
          </p>
          <h1 className="text-2xl md:text-3xl font-semibold tracking-tight text-neutral-900">
            {getGreeting()}, {user?.full_name?.split(' ')[0] || 'User'}
          </h1>
        </div>
        <Link href="/dashboard/history">
          <Button variant="outline" size="sm" className="gap-2">
            <Clock className="w-4 h-4" />
            View History
          </Button>
        </Link>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="shadow-sm hover:shadow-md transition-shadow">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-primary-50 flex items-center justify-center">
                <FileText className="w-5 h-5 text-primary-600" />
              </div>
              <div>
                <p className="text-2xl font-semibold text-neutral-900">{recentApplications.length}</p>
                <p className="text-xs text-neutral-500">Applications</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="shadow-sm hover:shadow-md transition-shadow">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-amber-50 flex items-center justify-center">
                <FileSearch className="w-5 h-5 text-amber-600" />
              </div>
              <div>
                <p className="text-2xl font-semibold text-neutral-900">{recentOfficeActions.length}</p>
                <p className="text-xs text-neutral-500">Office Actions</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="shadow-sm hover:shadow-md transition-shadow">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-50 flex items-center justify-center">
                <CheckCircle2 className="w-5 h-5 text-emerald-600" />
              </div>
              <div>
                <p className="text-2xl font-semibold text-neutral-900">{totalItems}</p>
                <p className="text-xs text-neutral-500">Total Processed</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="shadow-sm hover:shadow-md transition-shadow">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-rose-50 flex items-center justify-center">
                <BarChart3 className="w-5 h-5 text-rose-600" />
              </div>
              <div>
                <p className="text-2xl font-semibold text-neutral-900">{totalRejections}</p>
                <p className="text-xs text-neutral-500">Rejections Found</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Feature Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* ADS Generator */}
        <Card className="shadow-sm hover:shadow-lg transition-all duration-200 overflow-hidden group">
          <CardContent className="p-0">
            <div className="flex">
              {/* Left accent bar */}
              <div className="w-1 bg-primary-500" />
              <div className="p-5 flex-1">
                <div className="flex items-start gap-4">
                  <div className="w-11 h-11 rounded-xl bg-primary-500 flex items-center justify-center flex-shrink-0 shadow-sm">
                    <FileText className="w-5 h-5 text-white" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-neutral-900 mb-1">Application Data Sheets</h3>
                    <p className="text-sm text-neutral-500 mb-4 leading-relaxed">
                      Upload patent cover sheets to generate USPTO-compliant ADS forms with AI-powered extraction.
                    </p>
                    <Button asChild variant="primary" size="sm" className="group-hover:shadow-md transition-shadow">
                      <Link href="/dashboard/new-application">
                        Generate ADS
                        <ArrowRight className="w-3.5 h-3.5 ml-1.5 group-hover:translate-x-0.5 transition-transform" />
                      </Link>
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Office Action Analyzer */}
        <Card className="shadow-sm hover:shadow-lg transition-all duration-200 overflow-hidden group">
          <CardContent className="p-0">
            <div className="flex">
              {/* Left accent bar */}
              <div className="w-1 bg-amber-500" />
              <div className="p-5 flex-1">
                <div className="flex items-start gap-4">
                  <div className="w-11 h-11 rounded-xl bg-amber-500 flex items-center justify-center flex-shrink-0 shadow-sm">
                    <FileSearch className="w-5 h-5 text-white" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-neutral-900 mb-1">Office Action Analyzer</h3>
                    <p className="text-sm text-neutral-500 mb-4 leading-relaxed">
                      Extract rejections, deadlines, and prior art references. Generate response shells.
                    </p>
                    <Button asChild variant="outline" size="sm" className="border-amber-200 text-amber-700 hover:bg-amber-50 hover:border-amber-300 group-hover:shadow-sm transition-shadow">
                      <Link href="/dashboard/office-action">
                        Analyze Office Action
                        <ArrowRight className="w-3.5 h-3.5 ml-1.5 group-hover:translate-x-0.5 transition-transform" />
                      </Link>
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Recent Applications */}
        <Card className="shadow-sm">
          <CardHeader className="pb-3 border-b border-neutral-100">
            <div className="flex items-center justify-between">
              <CardTitle className="text-base font-medium flex items-center gap-2">
                <div className="w-6 h-6 rounded-md bg-primary-50 flex items-center justify-center">
                  <FileText className="w-3.5 h-3.5 text-primary-600" />
                </div>
                Recent Applications
              </CardTitle>
              {recentApplications.length > 0 && (
                <Link href="/dashboard/history" className="text-xs text-primary-600 hover:text-primary-700 font-medium hover:underline">
                  View all
                </Link>
              )}
            </div>
          </CardHeader>
          <CardContent className="pt-3">
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <div className="w-5 h-5 border-2 border-primary-200 border-t-primary-600 rounded-full animate-spin" />
              </div>
            ) : recentApplications.length === 0 ? (
              <div className="text-center py-8">
                <div className="w-12 h-12 rounded-full bg-neutral-50 flex items-center justify-center mx-auto mb-3">
                  <FileText className="w-6 h-6 text-neutral-300" />
                </div>
                <p className="text-sm text-neutral-500 mb-1">No applications yet</p>
                <p className="text-xs text-neutral-400">Generate your first ADS to see it here</p>
              </div>
            ) : (
              <div className="space-y-1">
                {recentApplications.map((app) => (
                  <Link
                    key={app._id}
                    href={`/dashboard/history/${app._id}`}
                    className="flex items-center justify-between p-3 -mx-3 rounded-lg hover:bg-neutral-50 transition-colors group"
                  >
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium text-neutral-900 truncate group-hover:text-primary-600 transition-colors">
                        {app.title || 'Untitled Application'}
                      </p>
                      <p className="text-xs text-neutral-400 mt-0.5">
                        {app.application_number || 'Draft'} · {formatRelativeDate(app.created_at)}
                      </p>
                    </div>
                    <ArrowRight className="w-4 h-4 text-neutral-300 group-hover:text-primary-500 group-hover:translate-x-0.5 transition-all flex-shrink-0 ml-3" />
                  </Link>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recent Office Actions */}
        <Card className="shadow-sm">
          <CardHeader className="pb-3 border-b border-neutral-100">
            <div className="flex items-center justify-between">
              <CardTitle className="text-base font-medium flex items-center gap-2">
                <div className="w-6 h-6 rounded-md bg-amber-50 flex items-center justify-center">
                  <FileSearch className="w-3.5 h-3.5 text-amber-600" />
                </div>
                Recent Office Actions
              </CardTitle>
              {recentOfficeActions.length > 0 && (
                <Link href="/dashboard/history" className="text-xs text-primary-600 hover:text-primary-700 font-medium hover:underline">
                  View all
                </Link>
              )}
            </div>
          </CardHeader>
          <CardContent className="pt-3">
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <div className="w-5 h-5 border-2 border-amber-200 border-t-amber-600 rounded-full animate-spin" />
              </div>
            ) : recentOfficeActions.length === 0 ? (
              <div className="text-center py-8">
                <div className="w-12 h-12 rounded-full bg-neutral-50 flex items-center justify-center mx-auto mb-3">
                  <FileSearch className="w-6 h-6 text-neutral-300" />
                </div>
                <p className="text-sm text-neutral-500 mb-1">No office actions yet</p>
                <p className="text-xs text-neutral-400">Analyze your first Office Action to see it here</p>
              </div>
            ) : (
              <div className="space-y-1">
                {recentOfficeActions.map((oa) => (
                  <Link
                    key={oa._id}
                    href={`/dashboard/office-action/${oa._id}/analysis`}
                    className="flex items-center justify-between p-3 -mx-3 rounded-lg hover:bg-neutral-50 transition-colors group"
                  >
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium text-neutral-900 truncate group-hover:text-amber-600 transition-colors">
                        {oa.application_number || oa.title_of_invention || 'Office Action'}
                      </p>
                      <div className="flex items-center gap-2 mt-0.5">
                        <p className="text-xs text-neutral-400">
                          {oa.office_action_type || 'Analysis'} · {formatRelativeDate(oa.created_at || '')}
                        </p>
                        {oa.total_rejections > 0 && (
                          <span className="inline-flex items-center text-[10px] font-medium text-amber-700 bg-amber-50 border border-amber-100 px-1.5 py-0.5 rounded">
                            {oa.total_rejections} rejection{oa.total_rejections !== 1 ? 's' : ''}
                          </span>
                        )}
                      </div>
                    </div>
                    <ArrowRight className="w-4 h-4 text-neutral-300 group-hover:text-amber-500 group-hover:translate-x-0.5 transition-all flex-shrink-0 ml-3" />
                  </Link>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Getting Started (only shown when no activity) */}
      {totalItems === 0 && !loading && (
        <Card className="border-dashed border-2 border-neutral-200 bg-neutral-50/50 shadow-none">
          <CardContent className="p-8 text-center">
            <div className="w-14 h-14 rounded-full bg-primary-50 flex items-center justify-center mx-auto mb-4">
              <Sparkles className="w-7 h-7 text-primary-500" />
            </div>
            <h3 className="font-semibold text-neutral-900 mb-1">Get Started with IP Automation</h3>
            <p className="text-sm text-neutral-500 mb-5 max-w-sm mx-auto">
              Choose a feature above to begin automating your patent workflow
            </p>
            <div className="flex items-center justify-center gap-3">
              <Button asChild variant="primary" size="sm">
                <Link href="/dashboard/new-application">
                  <FilePlus className="w-4 h-4 mr-1.5" />
                  Generate ADS
                </Link>
              </Button>
              <Button asChild variant="outline" size="sm">
                <Link href="/dashboard/office-action">
                  <FileSearch className="w-4 h-4 mr-1.5" />
                  Analyze Office Action
                </Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
