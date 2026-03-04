'use client';

import React, { useState, useRef } from 'react';
import { FileUpload } from './FileUpload';
import { InventorTable, Inventor } from './InventorTable';
import { ApplicantTable, Applicant } from './ApplicantTable';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { CheckCircle2, AlertTriangle, ArrowRight, Download, RefreshCw, Check } from 'lucide-react';
import api, { apiWithExtendedTimeout } from '@/lib/axios';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { cn } from '@/lib/utils';
import ValidationWarnings from '@/components/ValidationWarnings';
import { applicationsApi } from '@/lib/api/applications';

type WizardStep = 'upload' | 'review' | 'success';

interface CorrespondenceAddress {
  name?: string;
  name2?: string;
  address1?: string;
  address2?: string;
  city?: string;
  state?: string;
  country?: string;
  postcode?: string;
  phone?: string;
  fax?: string;
  email?: string;
  customer_number?: string;
}

interface ApplicationMetadata {
  title?: string;
  application_number?: string;
  entity_status?: string;
  inventors: Inventor[];
  applicants: Applicant[];
  total_drawing_sheets?: number;
  correspondence_address?: CorrespondenceAddress;
  application_type?: string;
  suggested_figure?: string;
  original_inventor_count?: number;
  is_figures_pdf?: boolean;
  figures_page_count?: number;
}

const steps = [
  { id: 'upload', name: 'Upload', description: 'Upload documents' },
  { id: 'review', name: 'Review', description: 'Verify data' },
  { id: 'success', name: 'Download', description: 'Get ADS' },
];

export const ApplicationWizard = () => {
  const [step, setStep] = useState<WizardStep>('upload');
  const [isLoading, setIsLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [processingStatus, setProcessingStatus] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [generateError, setGenerateError] = useState<{
    type: 'critical' | 'error' | 'warning';
    title: string;
    message: string;
  } | null>(null);

  const highestProgressRef = useRef<number>(0);
  const hasSavedToHistoryRef = useRef<boolean>(false);

  const setMonotonicProgress = (newProgress: number) => {
    if (newProgress > highestProgressRef.current) {
      highestProgressRef.current = newProgress;
      setUploadProgress(Math.round(newProgress));
    }
  };

  const resetProgress = () => {
    highestProgressRef.current = 0;
    setUploadProgress(0);
    hasSavedToHistoryRef.current = false;
  };

  const handleFileUploadError = (errorMessage: string) => {
    setError(errorMessage);
  };

  const [metadata, setMetadata] = useState<ApplicationMetadata>({
    inventors: [],
    applicants: [],
    correspondence_address: {
      name: '',
      address1: '',
      city: '',
      state: '',
      country: '',
      postcode: '',
      phone: '',
      email: '',
      customer_number: ''
    }
  });
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);

  const pollJobStatus = async (
    jobId: string,
    onProgress: (percent: number) => void
  ): Promise<void> => {
    const pollInterval = 2000;
    const maxAttempts = 60;

    for (let i = 0; i < maxAttempts; i++) {
      try {
        const response = await api.get(`/jobs/${jobId}`);
        const job = response.data;

        if (job.status === 'completed') {
          onProgress(100);
          return;
        } else if (job.status === 'failed') {
          throw new Error(job.error_details || 'Processing failed');
        }

        if (job.progress_percentage) {
          onProgress(job.progress_percentage);
        }

        await new Promise(resolve => setTimeout(resolve, pollInterval));
      } catch (err) {
        throw err;
      }
    }
    throw new Error('Processing timed out');
  };

  const handleFilesUpload = async (files: File[]) => {
    setIsLoading(true);
    resetProgress();
    setError(null);
    setGenerateError(null);
    setProcessingStatus('Starting...');

    const allResults: ApplicationMetadata[] = [];
    const totalFiles = files.length;
    
    const UPLOAD_PHASE_WEIGHT = 0.30;
    const PROCESS_PHASE_WEIGHT = 0.70;
    const perFileContribution = 100 / totalFiles;

    try {
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const fileIndex = i;
        
        const completedFilesProgress = (fileIndex / totalFiles) * 100;
        
        setProcessingStatus(`Uploading file ${i + 1} of ${totalFiles}: ${file.name}`);
        setMonotonicProgress(completedFilesProgress);

        const formData = new FormData();
        formData.append('file', file);
        const isCsv = file.name.toLowerCase().endsWith('.csv') || file.type === 'text/csv';

        const config = {
          headers: { 'Content-Type': 'multipart/form-data' },
          onUploadProgress: (progressEvent: any) => {
            const uploadPercent = progressEvent.total
              ? Math.round((progressEvent.loaded * 100) / progressEvent.total)
              : 0;
            
            const uploadContribution = (uploadPercent / 100) * UPLOAD_PHASE_WEIGHT * perFileContribution;
            const totalProgress = completedFilesProgress + uploadContribution;
            
            setMonotonicProgress(totalProgress);
          },
        };

        let fileResult: ApplicationMetadata;

        if (isCsv) {
          const response = await api.post('/applications/parse-csv', formData, config);
          fileResult = {
            inventors: response.data,
            title: '',
            application_number: '',
            applicants: []
          };
          
          const csvCompleteProgress = completedFilesProgress + perFileContribution;
          setMonotonicProgress(csvCompleteProgress);
          
        } else {
          formData.append('document_type', 'cover_sheet');
          const uploadResponse = await api.post('/documents/upload', formData, config);
          const documentId = uploadResponse.data.id || uploadResponse.data._id;

          const uploadCompleteProgress = completedFilesProgress + (UPLOAD_PHASE_WEIGHT * perFileContribution);
          setMonotonicProgress(uploadCompleteProgress);
          
          setProcessingStatus(`Extracting data from file ${i + 1} of ${totalFiles}: ${file.name}`);
          
          const parseResponse = await apiWithExtendedTimeout.post(`/documents/${documentId}/parse`);
          const jobId = parseResponse.data.job_id;

          await pollJobStatus(jobId, (processingPercent: number) => {
            const processingContribution = (processingPercent / 100) * PROCESS_PHASE_WEIGHT * perFileContribution;
            const totalProgress = uploadCompleteProgress + processingContribution;
            
            setMonotonicProgress(Math.min(totalProgress, 99));
            setProcessingStatus(
              `Extracting data from file ${i + 1} of ${totalFiles}: ${file.name} (${processingPercent}%)`
            );
          });

          const docResponse = await api.get(`/documents/${documentId}`);
          
          if (docResponse.data.extraction_data) {
            const extractionData = docResponse.data.extraction_data;
            
            fileResult = {
              title: extractionData.title || '',
              application_number: extractionData.application_number || '',
              entity_status: extractionData.entity_status || '',
              inventors: extractionData.inventors || [],
              applicants: extractionData.applicants || [],
              correspondence_address: extractionData.correspondence_address,
              application_type: extractionData.application_type,
              suggested_figure: extractionData.suggested_figure,
              total_drawing_sheets: extractionData.total_drawing_sheets ?? extractionData.figures_page_count ?? undefined,
              is_figures_pdf: extractionData.is_figures_pdf || false,
              figures_page_count: extractionData.figures_page_count,
            };
            
            if (fileResult.inventors && fileResult.inventors.length > 0) {
              fileResult.original_inventor_count = fileResult.inventors.length;
            }
          } else {
            throw new Error(`No extraction data found in ${file.name}`);
          }
        }

        allResults.push(fileResult);
        
        const fileCompleteProgress = ((fileIndex + 1) / totalFiles) * 100;
        setMonotonicProgress(fileCompleteProgress);
      }

      const mergedMetadata = mergeFileResults(allResults);
      
      setMetadata(mergedMetadata);
      setMonotonicProgress(100);
      setProcessingStatus('Complete!');
      setStep('review');

    } catch (err: any) {
      console.error('Processing failed:', err);
      let errorMessage = 'Failed to process files. Please try again.';

      if (err.response?.data?.detail) {
        const detail = err.response.data.detail;
        if (typeof detail === 'string') {
          errorMessage = detail;
        } else if (Array.isArray(detail)) {
          errorMessage = detail.map((e: any) => e.msg || JSON.stringify(e)).join(', ');
        } else if (typeof detail === 'object') {
          errorMessage = JSON.stringify(detail);
        }
      } else if (err.response?.data?.message) {
        errorMessage = err.response.data.message;
      } else if (err.message) {
         errorMessage = err.message;
      }

      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const mergeFileResults = (results: ApplicationMetadata[]): ApplicationMetadata => {
    const merged: ApplicationMetadata = {
      inventors: [],
      applicants: [],
      total_drawing_sheets: 0,
      correspondence_address: {
        name: '',
        address1: '',
        city: '',
        state: '',
        country: '',
        postcode: '',
        phone: '',
        email: '',
        customer_number: ''
      }
    };

    let originalInventorCount = 0;
    let totalDrawingSheets = 0;

    for (const result of results) {
      if (!merged.title && result.title) merged.title = result.title;
      if (!merged.application_number && result.application_number) merged.application_number = result.application_number;
      if (!merged.entity_status && result.entity_status) merged.entity_status = result.entity_status;
      if (!merged.application_type && result.application_type) merged.application_type = result.application_type;
      if (!merged.suggested_figure && result.suggested_figure) merged.suggested_figure = result.suggested_figure;
      if (result.correspondence_address && !merged.correspondence_address?.name) merged.correspondence_address = result.correspondence_address;
      
      if (result.applicants && result.applicants.length > 0) {
        for (const applicant of result.applicants) {
          const exists = merged.applicants.some(existing =>
            existing.name === applicant.name && existing.street_address === applicant.street_address
          );
          if (!exists) merged.applicants.push(applicant);
        }
      } else if ((result as any).applicant && (result as any).applicant.name) {
        const legacyApplicant = (result as any).applicant;
        const exists = merged.applicants.some(existing =>
          existing.name === legacyApplicant.name && existing.street_address === legacyApplicant.street_address
        );
        if (!exists) merged.applicants.push(legacyApplicant);
      }
      
      if (result.is_figures_pdf && result.figures_page_count) {
        totalDrawingSheets += result.figures_page_count;
      } else if (result.total_drawing_sheets && result.total_drawing_sheets > 0) {
        totalDrawingSheets += result.total_drawing_sheets;
      }
      
      if (result.inventors) {
        if (result.original_inventor_count && originalInventorCount === 0) {
          originalInventorCount = result.original_inventor_count;
        }
        
        for (const inventor of result.inventors) {
          const fullName = `${inventor.first_name || ''} ${inventor.middle_name || ''} ${inventor.last_name || ''}`.trim().toLowerCase();
          
          const exists = merged.inventors.some(existing => {
            const existingFullName = `${existing.first_name || ''} ${existing.middle_name || ''} ${existing.last_name || ''}`.trim().toLowerCase();
            if (existingFullName !== fullName) return false;
            
            const normalize = (val: string | undefined) => (val || '').trim().toLowerCase();
            const sameStreet = normalize(existing.street_address) === normalize(inventor.street_address) && normalize(inventor.street_address) !== '';
            const sameCity = normalize(existing.city) === normalize(inventor.city) && normalize(inventor.city) !== '';
            const sameState = normalize(existing.state) === normalize(inventor.state) && normalize(inventor.state) !== '';
            const sameZip = normalize(existing.zip_code) === normalize(inventor.zip_code) && normalize(inventor.zip_code) !== '';
            const addressMatch = sameStreet || (sameCity && sameState) || sameZip;
            const bothHaveNoAddress =
              !existing.street_address && !existing.city && !existing.state && !existing.zip_code &&
              !inventor.street_address && !inventor.city && !inventor.state && !inventor.zip_code;
            return addressMatch || bothHaveNoAddress;
          });

          if (!exists) merged.inventors.push(inventor);
        }
      }
    }

    merged.total_drawing_sheets = totalDrawingSheets > 0 ? totalDrawingSheets : undefined;
    if (merged.applicants.length === 0) merged.applicants.push({ name: '' });
    if (originalInventorCount > 0) merged.original_inventor_count = originalInventorCount;

    return merged;
  };

  const handleGenerateADS = async () => {
    if (isLoading) return;
    setIsLoading(true);
    setError(null);
    setGenerateError(null);
    setProcessingStatus('Generating PDF...');

    try {
      const response = await api.post('/applications/generate-ads', metadata, {
        responseType: 'blob',
      });

      const contentType = response.headers['content-type'] || '';
      
      if (contentType.includes('application/pdf')) {
        const blob = new Blob([response.data], { type: 'application/pdf' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;

        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const appNum = metadata.application_number?.replace(/[\/\\]/g, '-') || 'Draft';
        const filename = `ADS_${appNum}_${timestamp}.pdf`;

        link.setAttribute('download', filename);
        document.body.appendChild(link);

        setProcessingStatus('Download starting...');

        setTimeout(() => {
          link.click();
          setTimeout(() => {
              if (link.parentNode) link.parentNode.removeChild(link);
              window.URL.revokeObjectURL(url);
          }, 10000);

          setDownloadUrl(null);
          saveApplicationToHistory();
          setStep('success');
        }, 500);
      } else {
        const text = await response.data.text();
        let errorData;
        try { errorData = JSON.parse(text); } catch { errorData = { message: text }; }
        
        if (errorData.success === false && errorData.generation_blocked) {
          const message = errorData.message || '';
          if (message.includes('inventor_count_changed') || message.includes('Inventor count has changed')) {
            let cleanMessage = 'Inventor count has changed. Adding or removing inventors requires re-extraction.';
            if (message.includes('ADS generation failed: 400:')) {
              try {
                const errorPart = message.split('ADS generation failed: 400: ')[1];
                const jsonString = errorPart.replace(/'/g, '"');
                const errorObj = JSON.parse(jsonString);
                cleanMessage = errorObj.message || cleanMessage;
              } catch {
                if (message.includes('Inventor count has changed from')) {
                  const match = message.match(/Inventor count has changed from (\d+) to (\d+)/);
                  if (match) {
                    const [, originalCount, currentCount] = match;
                    cleanMessage = `Cannot generate ADS: Inventor count has changed from ${originalCount} to ${currentCount}. Adding or removing inventors requires re-extraction.`;
                  }
                }
              }
            }
            setGenerateError({ type: 'critical', title: 'Cannot Generate ADS', message: cleanMessage });
          } else {
            setGenerateError({ type: 'error', title: 'Generation Failed', message: errorData.message || 'Failed to generate ADS PDF.' });
          }
        } else {
          setGenerateError({ type: 'error', title: 'Generation Failed', message: 'An unexpected error occurred during PDF generation.' });
        }
        return;
      }

    } catch (error: any) {
      if (error.response?.status === 400) {
        let errorData;
        if (error.response.data instanceof Blob) {
          const text = await error.response.data.text();
          try { errorData = JSON.parse(text); } catch { errorData = { detail: { message: text } }; }
        } else {
          errorData = error.response.data;
        }
        
        if (errorData?.message && typeof errorData.message === 'object') {
          const errorObj = errorData.message;
          if (errorObj.error === 'inventor_count_changed') {
            setGenerateError({ type: 'critical', title: 'Cannot Generate ADS', message: errorObj.message });
          } else {
            setGenerateError({ type: 'error', title: 'Generation Failed', message: errorObj.message || 'Failed to generate ADS PDF.' });
          }
        } else {
          const detail = errorData?.detail;
          if (detail?.error === 'inventor_count_changed') {
            setGenerateError({ type: 'critical', title: 'Cannot Generate ADS', message: detail.message });
          } else {
            setGenerateError({ type: 'error', title: 'Generation Failed', message: detail?.message || detail || errorData?.message || 'Failed to generate ADS PDF.' });
          }
        }
      } else {
        console.error('Generation failed:', error);
        let errorMessage = 'Failed to generate ADS. Please try again.';
        if (error.response && error.response.data instanceof Blob) {
           try {
               const text = await error.response.data.text();
               const errorJson = JSON.parse(text);
               if (errorJson.detail) {
                   const detail = errorJson.detail;
                   if (typeof detail === 'string') errorMessage = detail;
                   else if (Array.isArray(detail)) errorMessage = detail.map((e: any) => e.msg || JSON.stringify(e)).join(', ');
                   else errorMessage = JSON.stringify(detail);
               }
           } catch (e) {}
        } else if (error.response?.data?.detail) {
          const detail = error.response.data.detail;
          if (typeof detail === 'string') errorMessage = detail;
          else if (Array.isArray(detail)) errorMessage = detail.map((e: any) => e.msg || JSON.stringify(e)).join(', ');
          else if (typeof detail === 'object') errorMessage = JSON.stringify(detail);
        }
        setError(errorMessage);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const saveApplicationToHistory = async () => {
    if (hasSavedToHistoryRef.current) return;
    hasSavedToHistoryRef.current = true;

    try {
      const enhancedData = {
        title: metadata.title,
        application_number: metadata.application_number,
        filing_date: new Date().toISOString(),
        entity_status: metadata.entity_status,
        attorney_docket_number: '',
        confirmation_number: '',
        application_type: metadata.application_type || 'utility',
        inventors: metadata.inventors.map((inv, index) => ({
          given_name: inv.first_name, middle_name: inv.middle_name, family_name: inv.last_name,
          full_name: `${inv.first_name || ''} ${inv.middle_name || ''} ${inv.last_name || ''}`.trim(),
          street_address: inv.street_address, address_line_2: '', city: inv.city, state: inv.state,
          postal_code: inv.zip_code, country: inv.country, citizenship: inv.citizenship,
          sequence_number: index + 1, completeness: 'complete', confidence_score: 0.95
        })),
        applicants: metadata.applicants.map((app) => ({
          is_assignee: true, organization_name: app.name, individual_given_name: '', individual_family_name: '',
          street_address: app.street_address, address_line_2: '', city: app.city, state: app.state,
          postal_code: app.zip_code, country: app.country, customer_number: '', email_address: '', phone_number: '',
          relationship_to_inventors: 'assignee', legal_entity_type: app.name ? 'corporation' : 'individual',
          completeness: 'complete', confidence_score: 0.95
        })),
        correspondence_info: metadata.correspondence_address ? {
          firm_name: metadata.correspondence_address.name, attorney_name: '',
          customer_number: metadata.correspondence_address.customer_number,
          email_address: metadata.correspondence_address.email,
          street_address: metadata.correspondence_address.address1,
          address_line_2: metadata.correspondence_address.address2,
          city: metadata.correspondence_address.city, state: metadata.correspondence_address.state,
          postal_code: metadata.correspondence_address.postcode, country: metadata.correspondence_address.country,
          phone_number: metadata.correspondence_address.phone, fax_number: metadata.correspondence_address.fax
        } : null,
        attorney_agent_info: null, domestic_priority_claims: [], foreign_priority_claims: [],
        classification_info: null,
        quality_metrics: {
          completeness_score: 0.95, accuracy_score: 0.95, confidence_score: 0.95, consistency_score: 0.95,
          overall_quality_score: 0.95, required_fields_populated: metadata.inventors.length + metadata.applicants.length,
          total_required_fields: metadata.inventors.length + metadata.applicants.length,
          optional_fields_populated: metadata.correspondence_address ? 1 : 0, total_optional_fields: 1,
          validation_errors: 0, validation_warnings: 0
        },
        extraction_metadata: {
          extraction_method: 'text_extraction', document_type: 'application_data_sheet',
          processing_time: 0, llm_tokens_used: 0, fallback_level_used: null,
          manual_review_required: false, extraction_notes: ['Application reviewed and ADS generated successfully']
        },
        manual_review_required: false, extraction_warnings: [], recommendations: [],
        field_validations: [], cross_field_validations: []
      };

      await api.post('/save-enhanced-application', enhancedData);
    } catch (error) {
      console.error('Failed to save application to history:', error);
    }
  };

  const resetWizard = () => {
    setStep('upload');
    setMetadata({
      inventors: [], applicants: [],
      correspondence_address: { name: '', address1: '', city: '', state: '', country: '', postcode: '', phone: '', email: '', customer_number: '' },
      original_inventor_count: undefined
    });
    setDownloadUrl(null);
    setError(null);
    setGenerateError(null);
    resetProgress();
  };

  const currentStepIndex = steps.findIndex(s => s.id === step);

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Progress Stepper */}
      <div className="flex items-center justify-center">
        <nav aria-label="Progress" className="w-full max-w-md">
          <ol className="flex items-center justify-between">
            {steps.map((s, index) => {
              const isComplete = index < currentStepIndex;
              const isCurrent = s.id === step;

              return (
                <li key={s.id} className="flex items-center">
                  <div className="flex flex-col items-center">
                    <div
                      className={cn(
                        "w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium transition-all duration-300",
                        isComplete
                          ? "bg-primary-500 text-white"
                          : isCurrent
                          ? "bg-primary-500 text-white ring-4 ring-primary-100 dark:ring-primary-900"
                          : "bg-neutral-100 dark:bg-neutral-800 text-neutral-500 dark:text-neutral-400"
                      )}
                    >
                      {isComplete ? <Check className="w-5 h-5" /> : index + 1}
                    </div>
                    <span
                      className={cn(
                        "mt-2 text-xs font-medium",
                        isCurrent ? "text-primary-600 dark:text-primary-400" : "text-neutral-500 dark:text-neutral-400"
                      )}
                    >
                      {s.name}
                    </span>
                  </div>
                  {index < steps.length - 1 && (
                    <div
                      className={cn(
                        "w-16 md:w-24 h-0.5 mx-2",
                        index < currentStepIndex ? "bg-primary-500" : "bg-neutral-200 dark:bg-neutral-700"
                      )}
                    />
                  )}
                </li>
              );
            })}
          </ol>
        </nav>
      </div>

      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 px-4 py-3 rounded-xl relative flex items-center gap-2">
          <AlertTriangle className="h-5 w-5 flex-shrink-0" />
          <span className="text-sm">{error}</span>
        </div>
      )}

      {step === 'upload' && (
        <div className="space-y-6">
          <div className="text-center space-y-2">
            <h2 className="text-2xl font-semibold tracking-tight text-neutral-900 dark:text-neutral-100">Upload Documents</h2>
            <p className="text-neutral-500 dark:text-neutral-400">Upload your Patent Cover Sheet (PDF) or Inventor List to get started.</p>
          </div>
          <FileUpload
            onFilesReady={handleFilesUpload}
            isLoading={isLoading}
            uploadProgress={uploadProgress}
            error={error}
            isProcessing={isLoading}
            onError={handleFileUploadError}
          />
          {isLoading && (
            <div className="w-full max-w-xl mx-auto space-y-2">
               {uploadProgress > 0 && (
                 <div className="h-2 w-full bg-neutral-100 dark:bg-neutral-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-primary-500 transition-all duration-300 ease-out"
                      style={{ width: `${uploadProgress}%` }}
                    />
                 </div>
               )}
               <div className="text-center text-sm text-neutral-500 dark:text-neutral-400 animate-pulse">
                  {processingStatus}
               </div>
            </div>
          )}
        </div>
      )}

      {step === 'review' && (
        <Card>
          <CardHeader>
            <CardTitle>Review Extracted Data</CardTitle>
            <CardDescription>
              Please verify the information below before generating the ADS.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <ValidationWarnings metadata={metadata} />

            {/* Application Title */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-neutral-700 dark:text-neutral-300">
                Application Title <span className="text-red-500">*</span>
              </label>
              <Textarea
                value={metadata.title || ''}
                onChange={(e) => setMetadata({...metadata, title: e.target.value})}
                placeholder="Enter the full application title..."
                className="min-h-[80px] text-base leading-relaxed resize-none"
                rows={3}
              />
              {metadata.title && (
                <p className="text-xs text-neutral-500 dark:text-neutral-400">
                  {metadata.title.length} characters
                </p>
              )}
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <label className="text-sm font-medium text-neutral-700 dark:text-neutral-300">Application Number</label>
                <Input
                  value={metadata.application_number || ''}
                  onChange={(e) => setMetadata({...metadata, application_number: e.target.value})}
                  placeholder="e.g. 17/123,456"
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-neutral-700 dark:text-neutral-300">Entity Status</label>
                <select
                  value={metadata.entity_status || ''}
                  onChange={(e) => setMetadata({...metadata, entity_status: e.target.value})}
                  className="flex h-10 w-full rounded-md border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-800 px-3 py-2 text-sm text-neutral-900 dark:text-neutral-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2 dark:focus-visible:ring-offset-neutral-900 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  <option value="">Select Entity Status</option>
                  <option value="Small Entity">Small Entity</option>
                  <option value="Micro Entity">Micro Entity</option>
                  <option value="Large Entity">Large Entity</option>
                </select>
              </div>
               <div className="space-y-2">
                <label className="text-sm font-medium text-neutral-700 dark:text-neutral-300">Total Drawing Sheets</label>
                <Input
                  type="number"
                  value={metadata.total_drawing_sheets || ''}
                  onChange={(e) => setMetadata({...metadata, total_drawing_sheets: parseInt(e.target.value) || 0})}
                  placeholder="Number of sheets"
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-neutral-700 dark:text-neutral-300">Application Type</label>
                <select
                  value={metadata.application_type || ''}
                  onChange={(e) => setMetadata({...metadata, application_type: e.target.value})}
                  className="flex h-10 w-full rounded-md border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-800 px-3 py-2 text-sm text-neutral-900 dark:text-neutral-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2 dark:focus-visible:ring-offset-neutral-900 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  <option value="">Select Application Type</option>
                  <option value="utility">Utility</option>
                  <option value="design">Design</option>
                  <option value="plant">Plant</option>
                  <option value="provisional">Provisional</option>
                  <option value="reissue">Reissue</option>
                </select>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-neutral-700 dark:text-neutral-300">Suggested Representative Figure</label>
                <Input
                  value={metadata.suggested_figure || ''}
                  onChange={(e) => setMetadata({...metadata, suggested_figure: e.target.value})}
                  placeholder="e.g. 1, 2A, 3B"
                />
              </div>
            </div>

            {/* Correspondence Address Section */}
            <div className="space-y-4 border border-neutral-200 dark:border-neutral-700 rounded-xl p-4 bg-blue-50/30 dark:bg-blue-900/10">
              <h3 className="font-medium text-base text-neutral-900 dark:text-neutral-100">
                📮 Correspondence Address (Law Firm/Attorney)
              </h3>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-neutral-700 dark:text-neutral-300">Firm/Attorney Name</label>
                  <Input value={metadata.correspondence_address?.name || ''} onChange={(e) => setMetadata({...metadata, correspondence_address: {...metadata.correspondence_address, name: e.target.value}})} placeholder="e.g. Blakely, Sokoloff, Taylor & Zafman LLP" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-neutral-700 dark:text-neutral-300">Customer Number</label>
                  <Input value={metadata.correspondence_address?.customer_number || ''} onChange={(e) => setMetadata({...metadata, correspondence_address: {...metadata.correspondence_address, customer_number: e.target.value}})} placeholder="USPTO Customer Number" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-neutral-700 dark:text-neutral-300">Street Address</label>
                  <Input value={metadata.correspondence_address?.address1 || ''} onChange={(e) => setMetadata({...metadata, correspondence_address: {...metadata.correspondence_address, address1: e.target.value}})} placeholder="Street address" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-neutral-700 dark:text-neutral-300">Address Line 2</label>
                  <Input value={metadata.correspondence_address?.address2 || ''} onChange={(e) => setMetadata({...metadata, correspondence_address: {...metadata.correspondence_address, address2: e.target.value}})} placeholder="Suite, floor, etc. (optional)" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-neutral-700 dark:text-neutral-300">City</label>
                  <Input value={metadata.correspondence_address?.city || ''} onChange={(e) => setMetadata({...metadata, correspondence_address: {...metadata.correspondence_address, city: e.target.value}})} placeholder="City" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-neutral-700 dark:text-neutral-300">State</label>
                  <Input value={metadata.correspondence_address?.state || ''} onChange={(e) => setMetadata({...metadata, correspondence_address: {...metadata.correspondence_address, state: e.target.value}})} placeholder="State (e.g. CA)" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-neutral-700 dark:text-neutral-300">Postal Code</label>
                  <Input value={metadata.correspondence_address?.postcode || ''} onChange={(e) => setMetadata({...metadata, correspondence_address: {...metadata.correspondence_address, postcode: e.target.value}})} placeholder="ZIP/Postal code" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-neutral-700 dark:text-neutral-300">Country</label>
                  <Input value={metadata.correspondence_address?.country || ''} onChange={(e) => setMetadata({...metadata, correspondence_address: {...metadata.correspondence_address, country: e.target.value}})} placeholder="Country" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-neutral-700 dark:text-neutral-300">Phone</label>
                  <Input value={metadata.correspondence_address?.phone || ''} onChange={(e) => setMetadata({...metadata, correspondence_address: {...metadata.correspondence_address, phone: e.target.value}})} placeholder="Phone number" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-neutral-700 dark:text-neutral-300">Email</label>
                  <Input value={metadata.correspondence_address?.email || ''} onChange={(e) => setMetadata({...metadata, correspondence_address: {...metadata.correspondence_address, email: e.target.value}})} placeholder="Email address" />
                </div>
              </div>
            </div>

            {/* Applicant Information Section */}
            <div className="space-y-4 border border-neutral-200 dark:border-neutral-700 rounded-xl p-4 bg-neutral-50/50 dark:bg-neutral-800/30">
                <h3 className="font-medium text-base text-neutral-900 dark:text-neutral-100">
                  Applicant / Company Information ({metadata.applicants.length})
                </h3>
                <ApplicantTable
                  applicants={metadata.applicants}
                  setApplicants={(applicants) => setMetadata({...metadata, applicants})}
                />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-neutral-700 dark:text-neutral-300">Inventors ({metadata.inventors.length})</label>
              <InventorTable
                inventors={metadata.inventors}
                setInventors={(invs) => setMetadata({...metadata, inventors: invs})}
              />
            </div>

            {/* Error display component */}
            {generateError && (
              <div className={`rounded-lg p-4 mb-4 ${
                generateError.type === 'critical'
                  ? 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800'
                  : 'bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800'
              }`}>
                <div className="flex items-start gap-3">
                  <svg
                    className={`w-5 h-5 mt-0.5 flex-shrink-0 ${
                      generateError.type === 'critical' ? 'text-red-500' : 'text-yellow-500'
                    }`}
                    fill="none" viewBox="0 0 24 24" stroke="currentColor"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <div>
                    <h4 className={`font-semibold ${
                      generateError.type === 'critical' ? 'text-red-800 dark:text-red-300' : 'text-yellow-800 dark:text-yellow-300'
                    }`}>
                      {generateError.title}
                    </h4>
                    <p className={`text-sm mt-1 ${
                      generateError.type === 'critical' ? 'text-red-700 dark:text-red-400' : 'text-yellow-700 dark:text-yellow-400'
                    }`}>
                      {generateError.message}
                    </p>
                  </div>
                  <button onClick={() => setGenerateError(null)} className="ml-auto text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-300">
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
            )}

            <div className="flex justify-end gap-4 pt-4 border-t border-neutral-100 dark:border-neutral-800">
              <Button variant="outline" onClick={() => setStep('upload')}>Back</Button>
              <Button variant="primary" onClick={handleGenerateADS} disabled={isLoading}>
                {isLoading ? (
                  <>
                    <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                    {processingStatus || 'Processing...'}
                  </>
                ) : (
                  <>
                    Generate ADS <ArrowRight className="ml-2 h-4 w-4" />
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {step === 'success' && (
        <Card className="text-center py-10">
          <CardContent className="space-y-6 flex flex-col items-center">
            <div className="h-20 w-20 bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 rounded-full flex items-center justify-center">
              <CheckCircle2 className="h-10 w-10" />
            </div>

            <div className="space-y-2">
              <h2 className="text-2xl font-semibold text-neutral-900 dark:text-neutral-100">ADS Generated Successfully!</h2>
              <p className="text-neutral-500 dark:text-neutral-400">Your Application Data Sheet has been downloaded.</p>
            </div>

            <div className="flex gap-4">
              <Button variant="outline" onClick={resetWizard}>Start Over</Button>
              {downloadUrl && (
                <Button variant="primary" asChild>
                  <a href={downloadUrl} target="_blank" rel="noopener noreferrer">
                    <Download className="mr-2 h-4 w-4" />
                    Download PDF
                  </a>
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

