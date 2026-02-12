'use client';

import React from 'react';
import { Input } from '@/components/ui/input';
import { AttorneyAgentInfo } from '@/lib/types';

interface AttorneyAgentInfoCardProps {
  attorneyInfo: AttorneyAgentInfo;
  setAttorneyInfo: (info: AttorneyAgentInfo) => void;
}

export const AttorneyAgentInfoCard: React.FC<AttorneyAgentInfoCardProps> = ({ 
  attorneyInfo, 
  setAttorneyInfo 
}) => {
  const handleInputChange = (field: keyof AttorneyAgentInfo, value: string | boolean) => {
    setAttorneyInfo({ ...attorneyInfo, [field]: value });
  };

  return (
    <div className="grid gap-4 md:grid-cols-2">
      <div className="space-y-2">
        <label className="text-sm font-medium text-neutral-700">Attorney/Agent Name</label>
        <Input
          value={attorneyInfo.name || ''}
          onChange={(e) => handleInputChange('name', e.target.value)}
          placeholder="Attorney/Agent Name"
        />
      </div>
      <div className="space-y-2">
        <label className="text-sm font-medium text-neutral-700">Registration Number</label>
        <Input
          value={attorneyInfo.registration_number || ''}
          onChange={(e) => handleInputChange('registration_number', e.target.value)}
          placeholder="Registration Number (e.g., 12,345)"
        />
      </div>
      <div className="space-y-2">
        <label className="text-sm font-medium text-neutral-700">Phone Number</label>
        <Input
          value={attorneyInfo.phone_number || ''}
          onChange={(e) => handleInputChange('phone_number', e.target.value)}
          placeholder="Phone Number"
        />
      </div>
      <div className="space-y-2">
        <label className="text-sm font-medium text-neutral-700">Email Address</label>
        <Input
          type="email"
          value={attorneyInfo.email_address || ''}
          onChange={(e) => handleInputChange('email_address', e.target.value)}
          placeholder="Email Address"
        />
      </div>
      <div className="space-y-2 md:col-span-2">
        <label className="text-sm font-medium text-neutral-700">Law Firm Name</label>
        <Input
          value={attorneyInfo.firm_name || ''}
          onChange={(e) => handleInputChange('firm_name', e.target.value)}
          placeholder="Law Firm Name"
        />
      </div>
      <div className="space-y-2 md:col-span-2">
        <label className="text-sm font-medium text-neutral-700">Type</label>
        <div className="flex gap-4">
          <label className="flex items-center space-x-2">
            <input
              type="radio"
              name="attorney_type"
              checked={attorneyInfo.is_attorney !== false}
              onChange={() => handleInputChange('is_attorney', true)}
              className="text-primary-600 focus:ring-primary-500"
            />
            <span className="text-sm text-neutral-700">Attorney</span>
          </label>
          <label className="flex items-center space-x-2">
            <input
              type="radio"
              name="attorney_type"
              checked={attorneyInfo.is_attorney === false}
              onChange={() => handleInputChange('is_attorney', false)}
              className="text-primary-600 focus:ring-primary-500"
            />
            <span className="text-sm text-neutral-700">Agent</span>
          </label>
        </div>
      </div>
    </div>
  );
};