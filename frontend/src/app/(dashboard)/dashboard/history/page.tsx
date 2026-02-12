'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Clock,
  FileText,
  Eye,
  Download,
  Calendar,
  User,
  Building,
  AlertCircle,
  Loader2,
  Scale,
  Gavel
} from 'lucide-react';
import { applicationsApi } from '@/lib/api/applications';
import { officeActionsApi } from '@/lib/api/officeActions';
import { ApplicationHistoryItem, OfficeActionHistoryItem, HistoryItem } from '@/lib/types';

type RecordTypeFilter = 'all' | 'application' | 'office_action';

export default function HistoryPage() {
  const router = useRouter();
  const [historyItems, setHistoryItems] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [filter, setFilter] = useState<RecordTypeFilter>('all');
  const limit = 10;

  useEffect(() => {
    loadHistory(true);
  }, []);

  const loadHistory = async (reset = false) => {
    try {
      if (reset) {
        setLoading(true);
        setError(null);
      } else {
        setLoadingMore(true);
      }

      const skip = reset ? 0 : page * limit;

      // Fetch both applications and office actions in parallel
      const [applications, officeActions] = await Promise.all([
        applicationsApi.getApplications({ skip, limit }),
        officeActionsApi.getOfficeActions({ skip, limit })
      ]);

      // Transform and combine
      const appItems: HistoryItem[] = applications.map(app => ({
        ...app,
        record_type: 'application' as const
      }));

      const oaItems: HistoryItem[] = officeActions.map(oa => ({
        ...oa,
        record_type: 'office_action' as const
      }));

      // Combine and sort by date (newest first)
      const combined = [...appItems, ...oaItems].sort((a, b) => {
        const dateA = new Date(a.created_at || 0);
        const dateB = new Date(b.created_at || 0);
        return dateB.getTime() - dateA.getTime();
      });

      if (reset) {
        setHistoryItems(combined);
        setPage(0);
      } else {
        setHistoryItems(prev => {
          // Merge and deduplicate
          const existingIds = new Set(prev.map(item => item._id));
          const newItems = combined.filter(item => !existingIds.has(item._id));
          return [...prev, ...newItems].sort((a, b) => {
            const dateA = new Date(a.created_at || 0);
            const dateB = new Date(b.created_at || 0);
            return dateB.getTime() - dateA.getTime();
          });
        });
      }

      // Check if there's more data
      setHasMore(applications.length === limit || officeActions.length === limit);
      if (!reset) setPage(prev => prev + 1);
    } catch (err) {
      setError('Failed to load history');
      console.error('Error loading history:', err);
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const handleDownloadADS = async (application: ApplicationHistoryItem) => {
    try {
      const blob = await applicationsApi.generateADSFromSaved(application._id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `ADS_${application.application_number || 'Draft'}_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Error downloading ADS:', err);
    }
  };

  const handleDownloadReport = async (officeAction: OfficeActionHistoryItem) => {
    try {
      const blob = await officeActionsApi.downloadReport(officeAction._id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Office_Action_Report_${officeAction.application_number || 'Document'}_${new Date().toISOString().split('T')[0]}.docx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Error downloading report:', err);
    }
  };

  // Filter items based on selected filter
  const filteredItems = historyItems.filter(item => {
    if (filter === 'all') return true;
    return item.record_type === filter;
  });

  // Count by type
  const applicationCount = historyItems.filter(i => i.record_type === 'application').length;
  const officeActionCount = historyItems.filter(i => i.record_type === 'office_action').length;

  if (loading && historyItems.length === 0) {
    return (
      <div className="space-y-6 animate-fade-in">
        <div>
          <h1 className="text-2xl md:text-3xl font-semibold tracking-tight text-neutral-900">
            History
          </h1>
          <p className="text-neutral-500 mt-1">
            View your previously processed documents
          </p>
        </div>
        <Card>
          <CardContent className="py-16">
            <div className="flex flex-col items-center justify-center text-center">
              <Loader2 className="w-8 h-8 text-neutral-400 animate-spin mb-4" />
              <p className="text-sm text-neutral-500">Loading history...</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6 animate-fade-in">
        <div>
          <h1 className="text-2xl md:text-3xl font-semibold tracking-tight text-neutral-900">
            History
          </h1>
          <p className="text-neutral-500 mt-1">
            View your previously processed documents
          </p>
        </div>
        <Card>
          <CardContent className="py-16">
            <div className="flex flex-col items-center justify-center text-center">
              <AlertCircle className="w-8 h-8 text-red-400 mb-4" />
              <h3 className="text-lg font-semibold text-neutral-900 mb-2">
                Error Loading History
              </h3>
              <p className="text-sm text-neutral-500 mb-4">{error}</p>
              <Button onClick={() => loadHistory(true)} variant="outline">
                Try Again
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (historyItems.length === 0) {
    return (
      <div className="space-y-6 animate-fade-in">
        <div>
          <h1 className="text-2xl md:text-3xl font-semibold tracking-tight text-neutral-900">
            History
          </h1>
          <p className="text-neutral-500 mt-1">
            View your previously processed documents
          </p>
        </div>
        <Card>
          <CardContent className="py-16">
            <div className="flex flex-col items-center justify-center text-center">
              <div className="w-16 h-16 rounded-full bg-neutral-100 flex items-center justify-center mb-4">
                <Clock className="w-8 h-8 text-neutral-400" />
              </div>
              <h3 className="text-lg font-semibold text-neutral-900 mb-2">
                No history yet
              </h3>
              <p className="text-sm text-neutral-500 max-w-sm">
                Your processed documents will appear here once you start generating Application Data Sheets or analyzing Office Actions.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-semibold tracking-tight text-neutral-900">
            History
          </h1>
          <p className="text-neutral-500 mt-1">
            View your previously processed documents ({filteredItems.length} {filter === 'all' ? 'total' : filter === 'application' ? 'applications' : 'office actions'})
          </p>
        </div>

        {/* Filter Buttons */}
        <div className="flex items-center gap-2">
          <Button
            variant={filter === 'all' ? 'primary' : 'outline'}
            size="sm"
            onClick={() => setFilter('all')}
          >
            All ({historyItems.length})
          </Button>
          <Button
            variant={filter === 'application' ? 'primary' : 'outline'}
            size="sm"
            onClick={() => setFilter('application')}
          >
            <FileText className="w-4 h-4 mr-1" />
            Applications ({applicationCount})
          </Button>
          <Button
            variant={filter === 'office_action' ? 'primary' : 'outline'}
            size="sm"
            onClick={() => setFilter('office_action')}
          >
            <Gavel className="w-4 h-4 mr-1" />
            Office Actions ({officeActionCount})
          </Button>
        </div>
      </div>

      {/* History List */}
      <div className="space-y-4">
        {filteredItems.map((item) => (
          item.record_type === 'application' ? (
            <ApplicationCard
              key={`app-${item._id}`}
              application={item}
              onView={() => router.push(`/dashboard/history/${item._id}`)}
              onDownload={() => handleDownloadADS(item)}
              formatDate={formatDate}
            />
          ) : (
            <OfficeActionCard
              key={`oa-${item._id}`}
              officeAction={item}
              onView={() => router.push(`/dashboard/office-action/${item._id}/analysis`)}
              onDownload={() => handleDownloadReport(item)}
              formatDate={formatDate}
            />
          )
        ))}
      </div>

      {/* Load More */}
      {hasMore && (
        <div className="flex justify-center">
          <Button
            variant="outline"
            onClick={() => loadHistory()}
            disabled={loadingMore}
          >
            {loadingMore ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Loading...
              </>
            ) : (
              'Load More'
            )}
          </Button>
        </div>
      )}
    </div>
  );
}

// Application Card Component
function ApplicationCard({
  application,
  onView,
  onDownload,
  formatDate
}: {
  application: ApplicationHistoryItem & { record_type: 'application' };
  onView: () => void;
  onDownload: () => void;
  formatDate: (date: string) => string;
}) {
  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          {/* Main Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0 mt-1">
                <FileText className="w-5 h-5 text-blue-600" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <Badge variant="default" className="bg-blue-100 text-blue-700 hover:bg-blue-100">
                    Application
                  </Badge>
                  {application.manual_review_required && (
                    <Badge variant="warning">
                      <AlertCircle className="w-3 h-3 mr-1" />
                      Review Required
                    </Badge>
                  )}
                </div>
                <h3 className="font-semibold text-neutral-900 truncate">
                  {application.title || 'Untitled Application'}
                </h3>
                <div className="flex flex-wrap items-center gap-4 mt-1 text-sm text-neutral-500">
                  {application.application_number && (
                    <span className="flex items-center gap-1">
                      <FileText className="w-3 h-3" />
                      {application.application_number}
                    </span>
                  )}
                  {application.filing_date && (
                    <span className="flex items-center gap-1">
                      <Calendar className="w-3 h-3" />
                      {formatDate(application.filing_date)}
                    </span>
                  )}
                  <span className="flex items-center gap-1">
                    <User className="w-3 h-3" />
                    {application.inventors.length} inventor{application.inventors.length !== 1 ? 's' : ''}
                  </span>
                  {application.applicants.length > 0 && (
                    <span className="flex items-center gap-1">
                      <Building className="w-3 h-3" />
                      {application.applicants.length} applicant{application.applicants.length !== 1 ? 's' : ''}
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2 flex-shrink-0">
            <Button variant="outline" size="sm" onClick={onView}>
              <Eye className="w-4 h-4 mr-2" />
              View Details
            </Button>
            <Button variant="primary" size="sm" onClick={onDownload}>
              <Download className="w-4 h-4 mr-2" />
              Download ADS
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// Office Action Card Component
function OfficeActionCard({
  officeAction,
  onView,
  onDownload,
  formatDate
}: {
  officeAction: OfficeActionHistoryItem & { record_type: 'office_action' };
  onView: () => void;
  onDownload: () => void;
  formatDate: (date: string) => string;
}) {
  // Get rejection type badges
  const rejectionBadges = Object.entries(officeAction.rejection_counts || {}).slice(0, 3);

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          {/* Main Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-lg bg-amber-100 flex items-center justify-center flex-shrink-0 mt-1">
                <Gavel className="w-5 h-5 text-amber-600" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <Badge variant="default" className="bg-amber-100 text-amber-700 hover:bg-amber-100">
                    Office Action
                  </Badge>
                  {officeAction.office_action_type && (
                    <Badge variant="outline">
                      {officeAction.office_action_type}
                    </Badge>
                  )}
                </div>
                <h3 className="font-semibold text-neutral-900 truncate">
                  {officeAction.title_of_invention || officeAction.filename || 'Untitled Office Action'}
                </h3>
                <div className="flex flex-wrap items-center gap-4 mt-1 text-sm text-neutral-500">
                  {officeAction.application_number && (
                    <span className="flex items-center gap-1">
                      <FileText className="w-3 h-3" />
                      {officeAction.application_number}
                    </span>
                  )}
                  {officeAction.office_action_date && (
                    <span className="flex items-center gap-1">
                      <Calendar className="w-3 h-3" />
                      {formatDate(officeAction.office_action_date)}
                    </span>
                  )}
                  {officeAction.examiner_name && (
                    <span className="flex items-center gap-1">
                      <User className="w-3 h-3" />
                      {officeAction.examiner_name}
                    </span>
                  )}
                  <span className="flex items-center gap-1">
                    <Scale className="w-3 h-3" />
                    {officeAction.total_rejections} rejection{officeAction.total_rejections !== 1 ? 's' : ''}
                  </span>
                </div>
                {/* Rejection type badges */}
                {rejectionBadges.length > 0 && (
                  <div className="flex flex-wrap items-center gap-1 mt-2">
                    {rejectionBadges.map(([type, count]) => (
                      <Badge key={type} variant="default" className="text-xs">
                        §{type} ({count})
                      </Badge>
                    ))}
                    {Object.keys(officeAction.rejection_counts || {}).length > 3 && (
                      <Badge variant="default" className="text-xs">
                        +{Object.keys(officeAction.rejection_counts).length - 3} more
                      </Badge>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2 flex-shrink-0">
            <Button variant="outline" size="sm" onClick={onView}>
              <Eye className="w-4 h-4 mr-2" />
              View Analysis
            </Button>
            <Button variant="primary" size="sm" onClick={onDownload}>
              <Download className="w-4 h-4 mr-2" />
              Download Report
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
