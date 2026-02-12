'use client';

import React from 'react';
import { Dialog, DialogContent } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  X,
  Download,
  FileText,
  User,
  Building,
  MapPin,
  Calendar,
  Hash,
  Globe
} from 'lucide-react';
import { ApplicationHistoryItem } from '@/lib/types';

interface ApplicationDetailModalProps {
  application: ApplicationHistoryItem;
  isOpen: boolean;
  onClose: () => void;
  onDownloadADS: (application: ApplicationHistoryItem) => void;
}

export function ApplicationDetailModal({
  application,
  isOpen,
  onClose,
  onDownloadADS
}: ApplicationDetailModalProps) {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[85vh] overflow-hidden p-0">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-neutral-200 p-6 pb-4">
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1 min-w-0">
              <h2 className="text-lg font-semibold text-neutral-900 leading-tight">
                {application.title || 'Untitled Application'}
              </h2>
              <div className="flex flex-wrap items-center gap-3 mt-2 text-sm text-neutral-500">
                {application.application_number && (
                  <span className="flex items-center gap-1.5">
                    <Hash className="w-3.5 h-3.5" />
                    {application.application_number}
                  </span>
                )}
                {application.filing_date && (
                  <span className="flex items-center gap-1.5">
                    <Calendar className="w-3.5 h-3.5" />
                    {formatDate(application.filing_date)}
                  </span>
                )}
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-neutral-100 rounded-lg transition-colors"
            >
              <X className="w-5 h-5 text-neutral-500" />
            </button>
          </div>

          {/* Status badges */}
          <div className="flex flex-wrap gap-2 mt-3">
            {application.entity_status && (
              <Badge variant="outline">{application.entity_status}</Badge>
            )}
            {application.application_type && (
              <Badge variant="outline" className="capitalize">{application.application_type}</Badge>
            )}
          </div>
        </div>

        {/* Content */}
        <div className="overflow-y-auto p-6 pt-4 space-y-6">
          {/* Inventors Section */}
          {application.inventors.length > 0 && (
            <div>
              <h3 className="flex items-center gap-2 text-sm font-semibold text-neutral-700 mb-3">
                <User className="w-4 h-4" />
                Inventors ({application.inventors.length})
              </h3>
              <div className="space-y-2">
                {application.inventors.map((inventor, index) => (
                  <div
                    key={index}
                    className="p-3 bg-neutral-50 rounded-lg border border-neutral-100"
                  >
                    <div className="font-medium text-neutral-900">
                      {inventor.full_name ||
                       `${inventor.given_name || ''} ${inventor.family_name || ''}`.trim() ||
                       'Unnamed Inventor'}
                    </div>
                    {(inventor.city || inventor.state || inventor.country) && (
                      <div className="flex items-center gap-1.5 mt-1 text-sm text-neutral-500">
                        <MapPin className="w-3 h-3" />
                        {[inventor.city, inventor.state, inventor.country]
                          .filter(Boolean)
                          .join(', ')}
                      </div>
                    )}
                    {inventor.citizenship && (
                      <div className="flex items-center gap-1.5 mt-1 text-sm text-neutral-500">
                        <Globe className="w-3 h-3" />
                        {inventor.citizenship}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Applicants Section */}
          {application.applicants.length > 0 && (
            <div>
              <h3 className="flex items-center gap-2 text-sm font-semibold text-neutral-700 mb-3">
                <Building className="w-4 h-4" />
                Applicants ({application.applicants.length})
              </h3>
              <div className="space-y-2">
                {application.applicants.map((applicant, index) => (
                  <div
                    key={index}
                    className="p-3 bg-neutral-50 rounded-lg border border-neutral-100"
                  >
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-neutral-900">
                        {applicant.organization_name ||
                         `${applicant.individual_given_name || ''} ${applicant.individual_family_name || ''}`.trim() ||
                         'Unnamed Applicant'}
                      </span>
                      {applicant.is_assignee && (
                        <Badge variant="primary" className="text-xs py-0">Assignee</Badge>
                      )}
                    </div>
                    {(applicant.city || applicant.state || applicant.country) && (
                      <div className="flex items-center gap-1.5 mt-1 text-sm text-neutral-500">
                        <MapPin className="w-3 h-3" />
                        {[applicant.city, applicant.state, applicant.country]
                          .filter(Boolean)
                          .join(', ')}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Additional Info */}
          {(application.attorney_docket_number || application.created_at) && (
            <div className="pt-4 border-t border-neutral-200">
              <div className="grid grid-cols-2 gap-4 text-sm">
                {application.attorney_docket_number && (
                  <div>
                    <span className="text-neutral-500">Docket Number</span>
                    <p className="font-medium text-neutral-900">{application.attorney_docket_number}</p>
                  </div>
                )}
                <div>
                  <span className="text-neutral-500">Processed</span>
                  <p className="font-medium text-neutral-900">{formatDate(application.created_at)}</p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 bg-white border-t border-neutral-200 p-4">
          <div className="flex justify-end gap-3">
            <Button variant="outline" onClick={onClose}>
              Close
            </Button>
            <Button variant="primary" onClick={() => onDownloadADS(application)}>
              <Download className="w-4 h-4 mr-2" />
              Download ADS
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
