'use client';

import React from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Trash2, Plus } from 'lucide-react';

export interface Inventor {
  first_name: string;
  middle_name?: string;
  last_name: string;
  suffix?: string;
  street_address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  country?: string;           // This is residence country (where they live)
  residence_country?: string; // Explicit residence country field
  citizenship?: string;       // This is citizenship/nationality (separate from residence)
}

interface InventorTableProps {
  inventors: Inventor[];
  setInventors: (inventors: Inventor[]) => void;
}

export const InventorTable: React.FC<InventorTableProps> = ({ inventors, setInventors }) => {
  
  const handleInputChange = (index: number, field: keyof Inventor, value: string) => {
    const newInventors = [...inventors];
    newInventors[index] = { ...newInventors[index], [field]: value };
    setInventors(newInventors);
  };

  const removeInventor = (index: number) => {
    const newInventors = inventors.filter((_, i) => i !== index);
    setInventors(newInventors);
  };

  const addInventor = () => {
    setInventors([...inventors, { first_name: '', last_name: '', citizenship: '', residence_country: '' }]);
  };

  return (
    <div className="w-full space-y-4">
      <div className="rounded-md border">
        <div className="w-full overflow-auto">
          <table className="w-full caption-bottom text-sm">
            <thead className="[&_tr]:border-b">
              <tr className="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
                <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground w-[25%]">Name</th>
                <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground w-[35%]">Address</th>
                <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground w-[25%]">Residence & Citizenship</th>
                <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground w-[50px]"></th>
              </tr>
            </thead>
            <tbody className="[&_tr:last-child]:border-0">
              {inventors.map((inventor, index) => (
                <tr key={index} className="border-b transition-colors hover:bg-muted/50">
                  <td className="p-4 align-middle">
                    <div className="space-y-2">
                        <div className="flex gap-1">
                            <Input
                            value={inventor.first_name || ''}
                            onChange={(e) => handleInputChange(index, 'first_name', e.target.value)}
                            placeholder="First"
                            className="flex-1 min-w-[100px]"
                            />
                            <Input
                            value={inventor.middle_name || ''}
                            onChange={(e) => handleInputChange(index, 'middle_name', e.target.value)}
                            placeholder="Middle"
                            className="w-28 min-w-[100px]"
                            />
                        </div>
                        <div className="flex gap-1">
                            <Input
                            value={inventor.last_name || ''}
                            onChange={(e) => handleInputChange(index, 'last_name', e.target.value)}
                            placeholder="Last / Family"
                            className="flex-1"
                            />
                             <Input
                             value={inventor.suffix || ''}
                             onChange={(e) => handleInputChange(index, 'suffix', e.target.value)}
                             placeholder="Sfx"
                             className="w-14"
                             disabled
                             style={{ display: 'none' }}
                             />
                        </div>
                    </div>
                  </td>
                  <td className="p-4 align-middle">
                    <div className="space-y-2">
                       <Input 
                        value={inventor.street_address || ''} 
                        onChange={(e) => handleInputChange(index, 'street_address', e.target.value)}
                        placeholder="Street Address"
                        className="mb-1"
                      />
                      <div className="flex gap-1">
                         <Input
                          value={inventor.city || ''}
                          onChange={(e) => handleInputChange(index, 'city', e.target.value)}
                          placeholder="City (e.g. San Francisco)"
                          className="flex-1 min-w-[140px]"
                        />
                         <Input
                          value={inventor.state || ''}
                          onChange={(e) => handleInputChange(index, 'state', e.target.value)}
                          placeholder="State"
                          className="w-20 min-w-[60px]"
                        />
                         <Input
                          value={inventor.zip_code || ''}
                          onChange={(e) => handleInputChange(index, 'zip_code', e.target.value)}
                          placeholder="Postal Code"
                          className="w-28 min-w-[90px]"
                        />
                      </div>
                      <div className="flex gap-1">
                         <Input
                          value={inventor.country || ''}
                          onChange={(e) => {
                            handleInputChange(index, 'country', e.target.value);
                            // Auto-sync residence_country with country for backward compatibility
                            handleInputChange(index, 'residence_country', e.target.value);
                          }}
                          placeholder="Residence Country"
                          className="flex-1"
                        />
                      </div>
                    </div>
                  </td>
                  <td className="p-4 align-middle">
                    <div className="space-y-2">
                      <Input
                        value={inventor.residence_country || inventor.country || ''}
                        onChange={(e) => {
                          handleInputChange(index, 'residence_country', e.target.value);
                          // Keep country field in sync for backward compatibility
                          handleInputChange(index, 'country', e.target.value);
                        }}
                        placeholder="Residence (where they live)"
                        className="min-w-[140px]"
                        title="Country where the inventor currently resides/lives"
                      />
                      <Input
                        value={inventor.citizenship || ''}
                        onChange={(e) => handleInputChange(index, 'citizenship', e.target.value)}
                        placeholder="Citizenship (nationality)"
                        className="min-w-[140px]"
                        title="Country of citizenship/nationality (can be different from residence)"
                      />
                    </div>
                  </td>
                  <td className="p-4 align-middle">
                    <Button 
                      variant="ghost" 
                      size="icon"
                      onClick={() => removeInventor(index)}
                      className="text-red-500 hover:text-red-700 hover:bg-red-50"
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
      <Button onClick={addInventor} variant="outline" className="w-full border-dashed">
        <Plus className="mr-2 h-4 w-4" /> Add Inventor
      </Button>
    </div>
  );
};