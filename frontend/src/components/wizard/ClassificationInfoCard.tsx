'use client';

import React from 'react';
import { Input } from '@/components/ui/input';
import { ClassificationInfo } from '@/lib/types';

interface ClassificationInfoCardProps {
  classificationInfo: ClassificationInfo;
  setClassificationInfo: (info: ClassificationInfo) => void;
}

export const ClassificationInfoCard: React.FC<ClassificationInfoCardProps> = ({ 
  classificationInfo, 
  setClassificationInfo 
}) => {
  const handleInputChange = (field: keyof ClassificationInfo, value: string) => {
    setClassificationInfo({ ...classificationInfo, [field]: value });
  };

  return (
    <div className="grid gap-4 md:grid-cols-2">
      <div className="space-y-2">
        <label className="text-sm font-medium text-neutral-700">Suggested Art Unit</label>
        <Input
          value={classificationInfo.suggested_art_unit || ''}
          onChange={(e) => handleInputChange('suggested_art_unit', e.target.value)}
          placeholder="Art Unit (e.g., 2100)"
        />
      </div>
      <div className="space-y-2">
        <label className="text-sm font-medium text-neutral-700">USPC Classification</label>
        <Input
          value={classificationInfo.uspc_classification || ''}
          onChange={(e) => handleInputChange('uspc_classification', e.target.value)}
          placeholder="USPC Classification"
        />
      </div>
      <div className="space-y-2">
        <label className="text-sm font-medium text-neutral-700">IPC Classification</label>
        <Input
          value={classificationInfo.ipc_classification || ''}
          onChange={(e) => handleInputChange('ipc_classification', e.target.value)}
          placeholder="IPC Classification"
        />
      </div>
      <div className="space-y-2">
        <label className="text-sm font-medium text-neutral-700">CPC Classification</label>
        <Input
          value={classificationInfo.cpc_classification || ''}
          onChange={(e) => handleInputChange('cpc_classification', e.target.value)}
          placeholder="CPC Classification"
        />
      </div>
    </div>
  );
};