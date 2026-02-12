'use client';

import React from 'react';
import { Input } from '@/components/ui/input';
import { CorrespondenceInfo } from '@/lib/types';

interface CorrespondenceInfoCardProps {
  correspondenceInfo: CorrespondenceInfo;
  setCorrespondenceInfo: (info: CorrespondenceInfo) => void;
}

export const CorrespondenceInfoCard: React.FC<CorrespondenceInfoCardProps> = ({ 
  correspondenceInfo, 
  setCorrespondenceInfo 
}) => {
  const handleInputChange = (field: keyof CorrespondenceInfo, value: string) => {
    setCorrespondenceInfo({ ...correspondenceInfo, [field]: value });
  };

  return (
    <div className="grid gap-4 md:grid-cols-2">
      <div className="space-y-2">
        <label className="text-sm font-medium text-neutral-700">Law Firm Name</label>
        <Input
          value={correspondenceInfo.firm_name || ''}
          onChange={(e) => handleInputChange('firm_name', e.target.value)}
          placeholder="Law Firm Name"
        />
      </div>
      <div className="space-y-2">
        <label className="text-sm font-medium text-neutral-700">Attorney Name</label>
        <Input
          value={correspondenceInfo.attorney_name || ''}
          onChange={(e) => handleInputChange('attorney_name', e.target.value)}
          placeholder="Attorney Name"
        />
      </div>
      <div className="space-y-2">
        <label className="text-sm font-medium text-neutral-700">Customer Number</label>
        <Input
          value={correspondenceInfo.customer_number || ''}
          onChange={(e) => handleInputChange('customer_number', e.target.value)}
          placeholder="Customer Number (5-6 digits)"
        />
      </div>
      <div className="space-y-2">
        <label className="text-sm font-medium text-neutral-700">Email Address</label>
        <Input
          type="email"
          value={correspondenceInfo.email_address || ''}
          onChange={(e) => handleInputChange('email_address', e.target.value)}
          placeholder="Email Address"
        />
      </div>
      <div className="space-y-2 md:col-span-2">
        <label className="text-sm font-medium text-neutral-700">Street Address</label>
        <Input
          value={correspondenceInfo.street_address || ''}
          onChange={(e) => handleInputChange('street_address', e.target.value)}
          placeholder="Street Address"
        />
      </div>
      <div className="space-y-2">
        <label className="text-sm font-medium text-neutral-700">Address Line 2</label>
        <Input
          value={correspondenceInfo.address_line_2 || ''}
          onChange={(e) => handleInputChange('address_line_2', e.target.value)}
          placeholder="Suite, Floor, etc."
        />
      </div>
      <div className="space-y-2">
        <label className="text-sm font-medium text-neutral-700">City</label>
        <Input
          value={correspondenceInfo.city || ''}
          onChange={(e) => handleInputChange('city', e.target.value)}
          placeholder="City"
        />
      </div>
      <div className="space-y-2">
        <label className="text-sm font-medium text-neutral-700">State</label>
        <Input
          value={correspondenceInfo.state || ''}
          onChange={(e) => handleInputChange('state', e.target.value)}
          placeholder="State"
        />
      </div>
      <div className="space-y-2">
        <label className="text-sm font-medium text-neutral-700">Postal Code</label>
        <Input
          value={correspondenceInfo.postal_code || ''}
          onChange={(e) => handleInputChange('postal_code', e.target.value)}
          placeholder="Postal Code"
        />
      </div>
      <div className="space-y-2">
        <label className="text-sm font-medium text-neutral-700">Country</label>
        <Input
          value={correspondenceInfo.country || ''}
          onChange={(e) => handleInputChange('country', e.target.value)}
          placeholder="Country (e.g., US)"
        />
      </div>
      <div className="space-y-2">
        <label className="text-sm font-medium text-neutral-700">Phone Number</label>
        <Input
          value={correspondenceInfo.phone_number || ''}
          onChange={(e) => handleInputChange('phone_number', e.target.value)}
          placeholder="Phone Number"
        />
      </div>
      <div className="space-y-2">
        <label className="text-sm font-medium text-neutral-700">Fax Number</label>
        <Input
          value={correspondenceInfo.fax_number || ''}
          onChange={(e) => handleInputChange('fax_number', e.target.value)}
          placeholder="Fax Number"
        />
      </div>
    </div>
  );
};