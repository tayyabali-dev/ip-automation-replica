'use client';

import { useState, useMemo } from 'react';

// ── Validation Logic ─────────────────────────────────────────────────────────

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

  // Application level validations
  if (!metadata.total_drawing_sheets) {
    warnings.push({
      field: 'total_drawing_sheets',
      message: "Total Drawing Sheets is empty — you'll need to fill this in manually.",
    });
  }

  if (!metadata.entity_status) {
    warnings.push({
      field: 'entity_status',
      message: 'Entity Status is not selected.',
    });
  }

  // Inventor validations
  if (metadata.inventors && metadata.inventors.length > 0) {
    metadata.inventors.forEach((inv, index) => {
      const invName = [inv.first_name, inv.last_name].filter(Boolean).join(' ') || `Inventor ${index + 1}`;
      
      // Check for residence country (check both 'country' and 'residence_country' fields)
      const hasResidence = inv.country;
      if (!hasResidence) {
        warnings.push({
          field: `inventor_${index}_residence`,
          message: `${invName}: Residence country not specified — will be left unselected in ADS.`,
        });
      }

      if (!inv.citizenship) {
        warnings.push({
          field: `inventor_${index}_citizenship`,
          message: `${invName}: Citizenship not specified.`,
        });
      }

      if (!inv.zip_code) {
        warnings.push({
          field: `inventor_${index}_postal`,
          message: `${invName}: Postal code is empty.`,
        });
      }

      if (!inv.street_address) {
        warnings.push({
          field: `inventor_${index}_address`,
          message: `${invName}: Street address is missing.`,
        });
      }

      if (!inv.city) {
        warnings.push({
          field: `inventor_${index}_city`,
          message: `${invName}: City is missing.`,
        });
      }
    });
  } else {
    warnings.push({
      field: 'inventors',
      message: 'No inventors found — at least one inventor is required.',
    });
  }

  // Correspondence address validations
  if (metadata.correspondence_address) {
    const corr = metadata.correspondence_address;
    
    if (!corr.name) {
      warnings.push({
        field: 'correspondence_name',
        message: 'Correspondence address: Firm/Attorney name is missing.',
      });
    }

    if (!corr.address1) {
      warnings.push({
        field: 'correspondence_address',
        message: 'Correspondence address: Street address is missing.',
      });
    }

    if (!corr.city) {
      warnings.push({
        field: 'correspondence_city',
        message: 'Correspondence address: City is missing.',
      });
    }
  }

  return warnings;
}

// ── Icons ────────────────────────────────────────────────────────────────────

function WarningIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 20 20" fill="none" style={{ flexShrink: 0 }}>
      <path
        d="M8.57465 3.21665L1.51632 14.9833C1.37079 15.2353 1.29379 15.5214 1.29298 15.8128C1.29216 16.1042 1.36756 16.3908 1.51167 16.6436C1.65579 16.8965 1.86359 17.1071 2.11441 17.2546C2.36523 17.4021 2.65058 17.4814 2.94198 17.4833H17.058C17.3494 17.4814 17.6347 17.4021 17.8856 17.2546C18.1364 17.1071 18.3442 16.8965 18.4883 16.6436C18.6324 16.3908 18.7078 16.1042 18.707 15.8128C18.7062 15.5214 18.6292 15.2353 18.4837 14.9833L11.4253 3.21665C11.2768 2.97174 11.0673 2.76928 10.8172 2.62924C10.567 2.4892 10.2843 2.41602 9.99698 2.41602C9.70963 2.41602 9.42694 2.4892 9.17681 2.62924C8.92668 2.76928 8.71714 2.97174 8.56865 3.21665H8.57465Z"
        stroke="#D97706" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"
      />
      <path d="M10 7.5V10.8333" stroke="#D97706" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M10 14.1667H10.0083" stroke="#D97706" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

// ── ValidationWarnings Component ─────────────────────────────────────────────

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
    <div style={{
      backgroundColor: '#FFFBEB', border: '1px solid #FCD34D', borderRadius: '8px',
      marginBottom: '20px', overflow: 'hidden',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 16px', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flex: 1 }}>
          <WarningIcon />
          <span style={{ fontSize: '14px', fontWeight: 500, color: '#92400E' }}>
            {warnings.length} field{warnings.length !== 1 ? 's' : ''} may need attention
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <button onClick={() => setExpanded(!expanded)} style={{
            display: 'flex', alignItems: 'center', gap: '4px', background: 'none', border: 'none',
            cursor: 'pointer', padding: '4px 8px', borderRadius: '4px', fontSize: '13px', fontWeight: 500, color: '#B45309',
          }}>
            {expanded ? 'Hide' : 'Show'}
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none"
              style={{ transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.2s ease' }}>
              <path d="M4 6L8 10L12 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
          <button onClick={() => { setDismissed(true); onDismiss?.(); }} style={{
            display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'none',
            border: 'none', cursor: 'pointer', padding: '4px', borderRadius: '4px', color: '#B45309',
          }}>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M4 4L12 12M12 4L4 12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
            </svg>
          </button>
        </div>
      </div>
      {expanded && (
        <div style={{ borderTop: '1px solid #FDE68A', padding: '12px 16px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {warnings.map((w, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
              <span style={{ color: '#D97706', fontWeight: 600, lineHeight: '1.5' }}>•</span>
              <span style={{ fontSize: '13px', color: '#78350F', lineHeight: '1.5' }}>{w.message}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ValidationWarnings;