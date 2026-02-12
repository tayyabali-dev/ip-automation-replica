'use client';

import React from 'react';
import { ApplicationWizard } from '@/components/wizard/ApplicationWizard';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function NewApplicationPage() {
  return (
    <div className="space-y-6 animate-fade-in">
      {/* Page Header */}
      <div className="flex items-center gap-4">
        <Link
          href="/dashboard"
          className="p-2 rounded-lg hover:bg-neutral-100 text-neutral-500 hover:text-neutral-900 transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-neutral-900">
            New Application
          </h1>
          <p className="text-sm text-neutral-500">
            Generate USPTO Application Data Sheet
          </p>
        </div>
      </div>

      {/* Wizard */}
      <ApplicationWizard />
    </div>
  );
}
