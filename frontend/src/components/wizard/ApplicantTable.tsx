'use client';

import React from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Trash2, Plus } from 'lucide-react';

export interface Applicant {
  name?: string;
  street_address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  country?: string;
}

interface ApplicantTableProps {
  applicants: Applicant[];
  setApplicants: (applicants: Applicant[]) => void;
}

export const ApplicantTable: React.FC<ApplicantTableProps> = ({ applicants, setApplicants }) => {
  
  const handleInputChange = (index: number, field: keyof Applicant, value: string) => {
    const newApplicants = [...applicants];
    newApplicants[index] = { ...newApplicants[index], [field]: value };
    setApplicants(newApplicants);
  };

  const removeApplicant = (index: number) => {
    const newApplicants = applicants.filter((_, i) => i !== index);
    setApplicants(newApplicants);
  };

  const addApplicant = () => {
    setApplicants([...applicants, { name: '' }]);
  };

  return (
    <div className="w-full space-y-4">
      <div className="rounded-md border">
        <div className="w-full overflow-auto">
          <table className="w-full caption-bottom text-sm">
            <thead className="[&_tr]:border-b">
              <tr className="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
                <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground w-[40%]">Name / Company</th>
                <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground w-[55%]">Address</th>
                <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground w-[50px]"></th>
              </tr>
            </thead>
            <tbody className="[&_tr:last-child]:border-0">
              {applicants.map((applicant, index) => (
                <tr key={index} className="border-b transition-colors hover:bg-muted/50">
                  <td className="p-4 align-middle">
                    <div className="space-y-2">
                      <Input
                        value={applicant.name || ''}
                        onChange={(e) => handleInputChange(index, 'name', e.target.value)}
                        placeholder="Applicant Name or Company"
                        className="w-full min-w-[250px]"
                      />
                    </div>
                  </td>
                  <td className="p-4 align-middle">
                    <div className="space-y-2">
                      <Input
                        value={applicant.street_address || ''}
                        onChange={(e) => handleInputChange(index, 'street_address', e.target.value)}
                        placeholder="Street Address"
                        className="mb-1 min-w-[200px]"
                      />
                      <div className="flex gap-1">
                        <Input
                          value={applicant.city || ''}
                          onChange={(e) => handleInputChange(index, 'city', e.target.value)}
                          placeholder="City"
                          className="flex-1 max-w-[140px]"
                        />
                        <Input
                          value={applicant.state || ''}
                          onChange={(e) => handleInputChange(index, 'state', e.target.value)}
                          placeholder="State"
                          className="w-24 min-w-[90px]"
                        />
                        <Input
                          value={applicant.zip_code || ''}
                          onChange={(e) => handleInputChange(index, 'zip_code', e.target.value)}
                          placeholder="Zip"
                          className="w-28 min-w-[100px]"
                        />
                      </div>
                      <Input
                        value={applicant.country || ''}
                        onChange={(e) => handleInputChange(index, 'country', e.target.value)}
                        placeholder="Country (e.g. US)"
                        className="flex-1"
                      />
                    </div>
                  </td>
                  <td className="p-4 align-middle">
                    <Button 
                      variant="ghost" 
                      size="icon"
                      onClick={() => removeApplicant(index)}
                      className="text-red-500 hover:text-red-700 hover:bg-red-50"
                      disabled={applicants.length === 1}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      <Button onClick={addApplicant} variant="outline" className="w-full border-dashed">
        <Plus className="mr-2 h-4 w-4" /> Add Applicant
      </Button>
    </div>
  );
};