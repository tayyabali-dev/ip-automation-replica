'use client';

import { useState, useMemo } from 'react';

interface ValidationWarning {
  field: string;
  message: string;
}

interface ApplicationMetadata {
  title?: string;
  application_number?: string;
  entity_status?: string;
  total_drawing_sheets?: number;
  inventors: Array<{
    first_name?: string;
    middle_name?: string;
    last_name?: string;
    street_address?: string;
    city?: string;
    state?: string;
    zip_code?: string;
    country?: string;
    citizenship?: string;
  }>;
  applicants: Array<{
    name?: string;
    street_address?: string;
    city?: string;
    state?: string;
    zip_code?: string;
    country?: string;
  }>;
  correspondence_address?: {
    name?: string;
    address1?: string;
    city?: string;
    state?: string;
    country?: string;
    postcode?: string;
    phone?: string;
    email?: string;
  };
  application_type?: string;
  suggested_figure?: string;
}

function validateMetadata(metadata: ApplicationMetadata): ValidationWarning[] {
  const warnings: ValidationWarning[] = [];

  if (!metadata.total_drawing_sheets) {
    warnings.push({ field: 'total_drawing_sheets', message: "Total Drawing Sheets is empty — you'll need to fill this in manually." });
  }
  if (!metadata.entity_status) {
    warnings.push({ field: 'entity_status', message: 'Entity Status is not selected.' });
  }

  if (metadata.inventors && metadata.inventors.length > 0) {
    metadata.inventors.forEach((inv, index) => {
      const invName = [inv.first_name, inv.last_name].filter(Boolean).join(' ') || `Inventor ${index + 1}`;
      if (!inv.country) warnings.push({ field: `inventor_${index}_residence`, message: `${invName}: Residence country not specified — will be left unselected in ADS.` });
      if (!inv.citizenship) warnings.push({ field: `inventor_${index}_citizenship`, message: `${invName}: Citizenship not specified.` });
      if (!inv.zip_code) warnings.push({ field: `inventor_${index}_postal`, message: `${invName}: Postal code is empty.` });
      if (!inv.street_address) warnings.push({ field: `inventor_${index}_address`, message: `${invName}: Street address is missing.` });
      if (!inv.city) warnings.push({ field: `inventor_${index}_city`, message: `${invName}: City is missing.` });
    });
  } else {
    warnings.push({ field: 'inventors', message: 'No inventors found — at least one inventor is required.' });
  }

  if (metadata.correspondence_address) {
    const corr = metadata.correspondence_address;
    if (!corr.name) warnings.push({ field: 'correspondence_name', message: 'Correspondence address: Firm/Attorney name is missing.' });
    if (!corr.address1) warnings.push({ field: 'correspondence_address', message: 'Correspondence address: Street address is missing.' });
    if (!corr.city) warnings.push({ field: 'correspondence_city', message: 'Correspondence address: City is missing.' });
  }

  return warnings;
}

interface ValidationWarningsProps {
  metadata: ApplicationMetadata;
  onDismiss?: () => void;
}

function ValidationWarnings({ metadata, onDismiss }: ValidationWarningsProps) {
  const [dismissed, setDismissed] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const warnings = useMemo(() => validateMetadata(metadata), [metadata]);

  if (warnings.length === 0 || dismissed) return null;

  return (
    <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-300 dark:border-amber-800 rounded-lg mb-5 overflow-hidden">
      <div className="flex items-center justify-between p-3 px-4 gap-3">
        <div className="flex items-center gap-2.5 flex-1">
          <svg width="18" height="18" viewBox="0 0 20 20" fill="none" className="flex-shrink-0">
            <path d="M8.57465 3.21665L1.51632 14.9833C1.37079 15.2353 1.29379 15.5214 1.29298 15.8128C1.29216 16.1042 1.36756 16.3908 1.51167 16.6436C1.65579 16.8965 1.86359 17.1071 2.11441 17.2546C2.36523 17.4021 2.65058 17.4814 2.94198 17.4833H17.058C17.3494 17.4814 17.6347 17.4021 17.8856 17.2546C18.1364 17.1071 18.3442 16.8965 18.4883 16.6436C18.6324 16.3908 18.7078 16.1042 18.707 15.8128C18.7062 15.5214 18.6292 15.2353 18.4837 14.9833L11.4253 3.21665C11.2768 2.97174 11.0673 2.76928 10.8172 2.62924C10.567 2.4892 10.2843 2.41602 9.99698 2.41602C9.70963 2.41602 9.42694 2.4892 9.17681 2.62924C8.92668 2.76928 8.71714 2.97174 8.56865 3.21665H8.57465Z" stroke="#D97706" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M10 7.5V10.8333" stroke="#D97706" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M10 14.1667H10.0083" stroke="#D97706" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          <span className="text-sm font-medium text-amber-800 dark:text-amber-300">
            {warnings.length} field{warnings.length !== 1 ? 's' : ''} may need attention
          </span>
        </div>
        <div className="flex items-center gap-1">
          <button onClick={() => setExpanded(!expanded)} className="flex items-center gap-1 bg-transparent border-none cursor-pointer py-1 px-2 rounded text-[13px] font-medium text-amber-700 dark:text-amber-400 hover:bg-amber-100 dark:hover:bg-amber-900/30 transition-colors">
            {expanded ? 'Hide' : 'Show'}
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" style={{ transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.2s ease' }}>
              <path d="M4 6L8 10L12 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
          <button onClick={() => { setDismissed(true); onDismiss?.(); }} className="flex items-center justify-center bg-transparent border-none cursor-pointer p-1 rounded text-amber-700 dark:text-amber-400 hover:bg-amber-100 dark:hover:bg-amber-900/30 transition-colors">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M4 4L12 12M12 4L4 12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
            </svg>
          </button>
        </div>
      </div>
      {expanded && (
        <div className="border-t border-amber-200 dark:border-amber-800 p-3 px-4 flex flex-col gap-2">
          {warnings.map((w, i) => (
            <div key={i} className="flex items-start gap-2">
              <span className="text-amber-600 dark:text-amber-500 font-semibold leading-relaxed">•</span>
              <span className="text-[13px] text-amber-900 dark:text-amber-300 leading-relaxed">{w.message}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ValidationWarnings;

