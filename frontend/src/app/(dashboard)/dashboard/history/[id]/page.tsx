'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import {
  ArrowLeft,
  Download,
  User,
  Building2,
  MapPin,
  Calendar,
  Globe,
  Loader2,
  AlertCircle,
  Clock,
  FileText,
  Mail,
  Phone,
  Briefcase,
  Scale,
  Link2,
  Flag,
  Hash,
  Layers
} from 'lucide-react';
import { applicationsApi } from '@/lib/api/applications';
import { ApplicationHistoryItem } from '@/lib/types';

export default function ApplicationDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [application, setApplication] = useState<ApplicationHistoryItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [downloading, setDownloading] = useState(false);

  const applicationId = params.id as string;

  useEffect(() => {
    if (applicationId) {
      loadApplication();
    }
  }, [applicationId]);

  const loadApplication = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await applicationsApi.getApplication(applicationId);
      setApplication(data);
    } catch (err) {
      setError('Failed to load application details');
      console.error('Error loading application:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const handleDownloadADS = async () => {
    if (!application) return;
    try {
      setDownloading(true);
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
    } finally {
      setDownloading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-6 h-6 text-primary-500 animate-spin" />
      </div>
    );
  }

  if (error || !application) {
    return (
      <div className="text-center py-16">
        <AlertCircle className="w-10 h-10 text-red-400 mx-auto mb-3" />
        <p className="text-neutral-600 mb-4">{error || 'Application not found'}</p>
        <Button variant="outline" size="sm" onClick={() => router.back()}>
          Go Back
        </Button>
      </div>
    );
  }

  const hasCorrespondence = application.correspondence_info && (
    application.correspondence_info.firm_name ||
    application.correspondence_info.attorney_name ||
    application.correspondence_info.email_address ||
    application.correspondence_info.phone_number
  );

  const hasAttorney = application.attorney_agent_info && (
    application.attorney_agent_info.name ||
    application.attorney_agent_info.registration_number
  );

  const hasDomesticPriority = application.domestic_priority_claims && application.domestic_priority_claims.length > 0;
  const hasForeignPriority = application.foreign_priority_claims && application.foreign_priority_claims.length > 0;

  const hasClassification = application.classification_info && (
    application.classification_info.suggested_art_unit ||
    application.classification_info.uspc_classification ||
    application.classification_info.cpc_classification
  );

  return (
    <div className="max-w-4xl mx-auto animate-fade-in">
      {/* Back Button */}
      <button
        onClick={() => router.back()}
        className="inline-flex items-center gap-1.5 text-neutral-500 hover:text-neutral-800 transition-colors mb-6 text-sm"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to History
      </button>

      {/* Header */}
      <div className="bg-white rounded-xl border border-neutral-200 p-5 mb-5">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            {/* Status */}
            <div className="flex items-center gap-2 mb-2 flex-wrap">
              {application.workflow_status && (
                <span className="text-xs font-medium text-primary-600 bg-primary-50 px-2 py-0.5 rounded-full capitalize">
                  {application.workflow_status}
                </span>
              )}
              {application.application_type && (
                <span className="text-xs font-medium text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full capitalize">
                  {application.application_type}
                </span>
              )}
              {application.entity_status && (
                <span className="text-xs text-neutral-500">
                  {application.entity_status}
                </span>
              )}
            </div>

            {/* Title */}
            <h1 className="text-lg font-semibold text-neutral-900 leading-snug mb-2">
              {application.title || 'Untitled Application'}
            </h1>

            {/* Meta */}
            <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-neutral-500">
              {application.application_number && (
                <span className="flex items-center gap-1.5">
                  <FileText className="w-3.5 h-3.5" />
                  {application.application_number}
                </span>
              )}
              {application.confirmation_number && (
                <span className="flex items-center gap-1.5">
                  <Hash className="w-3.5 h-3.5" />
                  Conf: {application.confirmation_number}
                </span>
              )}
              {application.filing_date && (
                <span className="flex items-center gap-1.5">
                  <Calendar className="w-3.5 h-3.5" />
                  {formatDate(application.filing_date)}
                </span>
              )}
              <span className="flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5" />
                Processed {formatDate(application.created_at)}
              </span>
            </div>
          </div>

          <Button
            variant="primary"
            size="sm"
            onClick={handleDownloadADS}
            disabled={downloading}
          >
            {downloading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <>
                <Download className="w-4 h-4 mr-1.5" />
                Download ADS
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Inventors & Applicants */}
      <div className="grid md:grid-cols-2 gap-5 mb-5">
        {/* Inventors */}
        <div className="bg-white rounded-xl border border-neutral-200 overflow-hidden">
          <div className="px-4 py-3 border-b border-neutral-100 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <User className="w-4 h-4 text-blue-600" />
              <span className="font-medium text-neutral-900 text-sm">Inventors</span>
            </div>
            <span className="text-xs text-neutral-400">{application.inventors.length}</span>
          </div>
          <div className="divide-y divide-neutral-100 max-h-64 overflow-y-auto">
            {application.inventors.length === 0 ? (
              <p className="p-4 text-sm text-neutral-400 text-center">No inventors</p>
            ) : (
              application.inventors.map((inventor, index) => (
                <div key={index} className="px-4 py-3 hover:bg-neutral-50 transition-colors">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-blue-50 flex items-center justify-center flex-shrink-0">
                      <span className="text-xs font-medium text-blue-700">
                        {(inventor.given_name?.[0] || inventor.full_name?.[0] || '?').toUpperCase()}
                      </span>
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium text-neutral-900 truncate">
                        {inventor.full_name ||
                         `${inventor.given_name || ''} ${inventor.family_name || ''}`.trim() ||
                         'Unnamed'}
                      </p>
                      {(inventor.city || inventor.country) && (
                        <p className="text-xs text-neutral-500 flex items-center gap-1 mt-0.5">
                          <MapPin className="w-3 h-3" />
                          {[inventor.city, inventor.country].filter(Boolean).join(', ')}
                        </p>
                      )}
                    </div>
                    {inventor.citizenship && (
                      <span className="text-xs text-neutral-400 flex items-center gap-1">
                        <Globe className="w-3 h-3" />
                        {inventor.citizenship}
                      </span>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Applicants */}
        <div className="bg-white rounded-xl border border-neutral-200 overflow-hidden">
          <div className="px-4 py-3 border-b border-neutral-100 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Building2 className="w-4 h-4 text-purple-600" />
              <span className="font-medium text-neutral-900 text-sm">Applicants</span>
            </div>
            <span className="text-xs text-neutral-400">{application.applicants.length}</span>
          </div>
          <div className="divide-y divide-neutral-100 max-h-64 overflow-y-auto">
            {application.applicants.length === 0 ? (
              <p className="p-4 text-sm text-neutral-400 text-center">No applicants</p>
            ) : (
              application.applicants.map((applicant, index) => (
                <div key={index} className="px-4 py-3 hover:bg-neutral-50 transition-colors">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-purple-50 flex items-center justify-center flex-shrink-0">
                      <Building2 className="w-3.5 h-3.5 text-purple-600" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2">
                        <p className="text-sm font-medium text-neutral-900 truncate">
                          {applicant.organization_name ||
                           `${applicant.individual_given_name || ''} ${applicant.individual_family_name || ''}`.trim() ||
                           'Unnamed'}
                        </p>
                        {applicant.is_assignee && (
                          <span className="text-[10px] font-medium text-primary-700 bg-primary-50 px-1.5 py-0.5 rounded">
                            Assignee
                          </span>
                        )}
                      </div>
                      {(applicant.city || applicant.country) && (
                        <p className="text-xs text-neutral-500 flex items-center gap-1 mt-0.5">
                          <MapPin className="w-3 h-3" />
                          {[applicant.city, applicant.country].filter(Boolean).join(', ')}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Correspondence & Attorney Info */}
      {(hasCorrespondence || hasAttorney) && (
        <div className="grid md:grid-cols-2 gap-5 mb-5">
          {/* Correspondence */}
          {hasCorrespondence && (
            <div className="bg-white rounded-xl border border-neutral-200 p-4">
              <div className="flex items-center gap-2 mb-3">
                <Mail className="w-4 h-4 text-green-600" />
                <span className="font-medium text-neutral-900 text-sm">Correspondence</span>
              </div>
              <div className="space-y-2 text-sm">
                {application.correspondence_info?.firm_name && (
                  <p className="font-medium text-neutral-900">{application.correspondence_info.firm_name}</p>
                )}
                {application.correspondence_info?.attorney_name && (
                  <p className="text-neutral-600">{application.correspondence_info.attorney_name}</p>
                )}
                {application.correspondence_info?.customer_number && (
                  <p className="text-neutral-500 text-xs">Customer #: {application.correspondence_info.customer_number}</p>
                )}
                <div className="flex flex-wrap gap-3 pt-1">
                  {application.correspondence_info?.email_address && (
                    <span className="flex items-center gap-1 text-xs text-neutral-500">
                      <Mail className="w-3 h-3" />
                      {application.correspondence_info.email_address}
                    </span>
                  )}
                  {application.correspondence_info?.phone_number && (
                    <span className="flex items-center gap-1 text-xs text-neutral-500">
                      <Phone className="w-3 h-3" />
                      {application.correspondence_info.phone_number}
                    </span>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Attorney/Agent */}
          {hasAttorney && (
            <div className="bg-white rounded-xl border border-neutral-200 p-4">
              <div className="flex items-center gap-2 mb-3">
                <Scale className="w-4 h-4 text-amber-600" />
                <span className="font-medium text-neutral-900 text-sm">Attorney/Agent</span>
              </div>
              <div className="space-y-2 text-sm">
                {application.attorney_agent_info?.name && (
                  <p className="font-medium text-neutral-900">{application.attorney_agent_info.name}</p>
                )}
                {application.attorney_agent_info?.firm_name && (
                  <p className="text-neutral-600">{application.attorney_agent_info.firm_name}</p>
                )}
                {application.attorney_agent_info?.registration_number && (
                  <p className="text-neutral-500 text-xs">Reg #: {application.attorney_agent_info.registration_number}</p>
                )}
                <div className="flex flex-wrap gap-3 pt-1">
                  {application.attorney_agent_info?.email_address && (
                    <span className="flex items-center gap-1 text-xs text-neutral-500">
                      <Mail className="w-3 h-3" />
                      {application.attorney_agent_info.email_address}
                    </span>
                  )}
                  {application.attorney_agent_info?.phone_number && (
                    <span className="flex items-center gap-1 text-xs text-neutral-500">
                      <Phone className="w-3 h-3" />
                      {application.attorney_agent_info.phone_number}
                    </span>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Priority Claims */}
      {(hasDomesticPriority || hasForeignPriority) && (
        <div className="grid md:grid-cols-2 gap-5 mb-5">
          {/* Domestic Priority */}
          {hasDomesticPriority && (
            <div className="bg-white rounded-xl border border-neutral-200 overflow-hidden">
              <div className="px-4 py-3 border-b border-neutral-100 flex items-center gap-2">
                <Link2 className="w-4 h-4 text-indigo-600" />
                <span className="font-medium text-neutral-900 text-sm">Domestic Priority</span>
              </div>
              <div className="divide-y divide-neutral-100">
                {application.domestic_priority_claims.map((claim, index) => (
                  <div key={index} className="px-4 py-3">
                    <p className="text-sm font-medium text-neutral-900">{claim.application_number}</p>
                    <div className="flex items-center gap-3 mt-1 text-xs text-neutral-500">
                      {claim.filing_date && (
                        <span className="flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          {formatDate(claim.filing_date)}
                        </span>
                      )}
                      {claim.continuity_type && (
                        <span className="capitalize">{claim.continuity_type}</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Foreign Priority */}
          {hasForeignPriority && (
            <div className="bg-white rounded-xl border border-neutral-200 overflow-hidden">
              <div className="px-4 py-3 border-b border-neutral-100 flex items-center gap-2">
                <Flag className="w-4 h-4 text-rose-600" />
                <span className="font-medium text-neutral-900 text-sm">Foreign Priority</span>
              </div>
              <div className="divide-y divide-neutral-100">
                {application.foreign_priority_claims.map((claim, index) => (
                  <div key={index} className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <p className="text-sm font-medium text-neutral-900">{claim.application_number}</p>
                      {claim.country && (
                        <span className="text-xs bg-neutral-100 text-neutral-600 px-1.5 py-0.5 rounded">
                          {claim.country}
                        </span>
                      )}
                    </div>
                    {claim.filing_date && (
                      <p className="flex items-center gap-1 mt-1 text-xs text-neutral-500">
                        <Calendar className="w-3 h-3" />
                        {formatDate(claim.filing_date)}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Classification & Additional Info */}
      {(hasClassification || application.attorney_docket_number) && (
        <div className="bg-white rounded-xl border border-neutral-200 p-4 mb-5">
          <div className="flex items-center gap-2 mb-3">
            <Layers className="w-4 h-4 text-teal-600" />
            <span className="font-medium text-neutral-900 text-sm">Additional Details</span>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            {application.attorney_docket_number && (
              <div>
                <p className="text-xs text-neutral-500 mb-0.5">Docket Number</p>
                <p className="font-medium text-neutral-900">{application.attorney_docket_number}</p>
              </div>
            )}
            {application.classification_info?.suggested_art_unit && (
              <div>
                <p className="text-xs text-neutral-500 mb-0.5">Art Unit</p>
                <p className="font-medium text-neutral-900">{application.classification_info.suggested_art_unit}</p>
              </div>
            )}
            {application.classification_info?.uspc_classification && (
              <div>
                <p className="text-xs text-neutral-500 mb-0.5">USPC</p>
                <p className="font-medium text-neutral-900">{application.classification_info.uspc_classification}</p>
              </div>
            )}
            {application.classification_info?.cpc_classification && (
              <div>
                <p className="text-xs text-neutral-500 mb-0.5">CPC</p>
                <p className="font-medium text-neutral-900">{application.classification_info.cpc_classification}</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Extraction Warnings */}
      {application.extraction_warnings && application.extraction_warnings.length > 0 && (
        <div className="bg-amber-50 rounded-xl border border-amber-200 p-4 mb-5">
          <div className="flex items-center gap-2 mb-3">
            <AlertCircle className="w-4 h-4 text-amber-600" />
            <span className="font-medium text-amber-900 text-sm">Extraction Warnings</span>
          </div>
          <ul className="space-y-1.5">
            {application.extraction_warnings.map((warning, index) => (
              <li key={index} className="text-sm text-amber-800 flex items-start gap-2">
                <span className="text-amber-400 mt-1">•</span>
                {warning}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Recommendations */}
      {application.recommendations && application.recommendations.length > 0 && (
        <div className="bg-blue-50 rounded-xl border border-blue-200 p-4 mb-5">
          <div className="flex items-center gap-2 mb-3">
            <Briefcase className="w-4 h-4 text-blue-600" />
            <span className="font-medium text-blue-900 text-sm">Recommendations</span>
          </div>
          <ul className="space-y-1.5">
            {application.recommendations.map((rec, index) => (
              <li key={index} className="text-sm text-blue-800 flex items-start gap-2">
                <span className="text-blue-400 mt-1">•</span>
                {rec}
              </li>
            ))}
          </ul>
        </div>
      )}

    </div>
  );
}
