'use client';

import React from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Trash2, Plus } from 'lucide-react';
import { DomesticPriorityClaim, ForeignPriorityClaim } from '@/lib/types';

interface PriorityClaimsTableProps {
  domesticClaims: DomesticPriorityClaim[];
  foreignClaims: ForeignPriorityClaim[];
  setDomesticClaims: (claims: DomesticPriorityClaim[]) => void;
  setForeignClaims: (claims: ForeignPriorityClaim[]) => void;
}

export const PriorityClaimsTable: React.FC<PriorityClaimsTableProps> = ({ 
  domesticClaims, 
  foreignClaims, 
  setDomesticClaims, 
  setForeignClaims 
}) => {
  
  const addDomesticClaim = () => {
    setDomesticClaims([...domesticClaims, {}]);
  };

  const addForeignClaim = () => {
    setForeignClaims([...foreignClaims, {}]);
  };

  const removeDomesticClaim = (index: number) => {
    setDomesticClaims(domesticClaims.filter((_, i) => i !== index));
  };

  const removeForeignClaim = (index: number) => {
    setForeignClaims(foreignClaims.filter((_, i) => i !== index));
  };

  const updateDomesticClaim = (index: number, field: keyof DomesticPriorityClaim, value: string) => {
    const newClaims = [...domesticClaims];
    newClaims[index] = { ...newClaims[index], [field]: value };
    setDomesticClaims(newClaims);
  };

  const updateForeignClaim = (index: number, field: keyof ForeignPriorityClaim, value: string | boolean | undefined) => {
    const newClaims = [...foreignClaims];
    newClaims[index] = { ...newClaims[index], [field]: value };
    setForeignClaims(newClaims);
  };

  return (
    <div className="space-y-6">
      {/* Domestic Priority Claims */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h4 className="font-medium text-neutral-900">Domestic Benefit Claims</h4>
          <Button onClick={addDomesticClaim} variant="outline" size="sm">
            <Plus className="mr-2 h-4 w-4" /> Add Domestic Claim
          </Button>
        </div>
        
        {domesticClaims.map((claim, index) => (
          <div key={index} className="border rounded-lg p-4 space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">Domestic Claim {index + 1}</span>
              <Button 
                variant="ghost" 
                size="sm"
                onClick={() => removeDomesticClaim(index)}
                className="text-red-500 hover:text-red-700"
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
            <div className="grid gap-3 md:grid-cols-2">
              <div className="space-y-2">
                <label className="text-xs font-medium text-neutral-600">Parent Application Number</label>
                <Input
                  value={claim.parent_application_number || ''}
                  onChange={(e) => updateDomesticClaim(index, 'parent_application_number', e.target.value)}
                  placeholder="Parent Application Number"
                />
              </div>
              <div className="space-y-2">
                <label className="text-xs font-medium text-neutral-600">Filing Date</label>
                <Input
                  type="date"
                  value={claim.filing_date || ''}
                  onChange={(e) => updateDomesticClaim(index, 'filing_date', e.target.value)}
                  placeholder="Filing Date"
                />
              </div>
              <div className="space-y-2">
                <label className="text-xs font-medium text-neutral-600">Application Type</label>
                <select
                  value={claim.application_type || ''}
                  onChange={(e) => updateDomesticClaim(index, 'application_type', e.target.value)}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                >
                  <option value="">Select Type</option>
                  <option value="provisional">Provisional</option>
                  <option value="nonprovisional">Nonprovisional</option>
                  <option value="pct">PCT</option>
                </select>
              </div>
              <div className="space-y-2">
                <label className="text-xs font-medium text-neutral-600">Relationship Type</label>
                <select
                  value={claim.relationship_type || ''}
                  onChange={(e) => updateDomesticClaim(index, 'relationship_type', e.target.value)}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                >
                  <option value="">Select Relationship</option>
                  <option value="continuation">Continuation</option>
                  <option value="divisional">Divisional</option>
                  <option value="cip">Continuation-in-Part</option>
                </select>
              </div>
              <div className="space-y-2 md:col-span-2">
                <label className="text-xs font-medium text-neutral-600">Status</label>
                <select
                  value={claim.status || ''}
                  onChange={(e) => updateDomesticClaim(index, 'status', e.target.value)}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                >
                  <option value="">Select Status</option>
                  <option value="pending">Pending</option>
                  <option value="patented">Patented</option>
                  <option value="abandoned">Abandoned</option>
                </select>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Foreign Priority Claims */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h4 className="font-medium text-neutral-900">Foreign Priority Claims</h4>
          <Button onClick={addForeignClaim} variant="outline" size="sm">
            <Plus className="mr-2 h-4 w-4" /> Add Foreign Claim
          </Button>
        </div>
        
        {foreignClaims.map((claim, index) => (
          <div key={index} className="border rounded-lg p-4 space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">Foreign Claim {index + 1}</span>
              <Button 
                variant="ghost" 
                size="sm"
                onClick={() => removeForeignClaim(index)}
                className="text-red-500 hover:text-red-700"
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
            <div className="grid gap-3 md:grid-cols-3">
              <div className="space-y-2">
                <label className="text-xs font-medium text-neutral-600">Country Code</label>
                <Input
                  value={claim.country_code || ''}
                  onChange={(e) => updateForeignClaim(index, 'country_code', e.target.value)}
                  placeholder="Country Code (e.g., EP, JP)"
                />
              </div>
              <div className="space-y-2">
                <label className="text-xs font-medium text-neutral-600">Application Number</label>
                <Input
                  value={claim.application_number || ''}
                  onChange={(e) => updateForeignClaim(index, 'application_number', e.target.value)}
                  placeholder="Application Number"
                />
              </div>
              <div className="space-y-2">
                <label className="text-xs font-medium text-neutral-600">Filing Date</label>
                <Input
                  type="date"
                  value={claim.filing_date || ''}
                  onChange={(e) => updateForeignClaim(index, 'filing_date', e.target.value)}
                  placeholder="Filing Date"
                />
              </div>
              <div className="space-y-2 md:col-span-2">
                <label className="text-xs font-medium text-neutral-600">Certified Copy Status</label>
                <Input
                  value={claim.certified_copy_status || ''}
                  onChange={(e) => updateForeignClaim(index, 'certified_copy_status', e.target.value)}
                  placeholder="Certified Copy Status"
                />
              </div>
              <div className="space-y-2">
                <label className="text-xs font-medium text-neutral-600">Certified Copy Filed</label>
                <select
                  value={claim.certified_copy_filed === true ? 'true' : claim.certified_copy_filed === false ? 'false' : ''}
                  onChange={(e) => updateForeignClaim(index, 'certified_copy_filed', e.target.value === 'true' ? true : e.target.value === 'false' ? false : undefined)}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                >
                  <option value="">Select</option>
                  <option value="true">Yes</option>
                  <option value="false">No</option>
                </select>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};