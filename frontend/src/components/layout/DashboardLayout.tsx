'use client';

import React from 'react';
import { Sidebar } from './Sidebar';
import { MobileHeader } from './MobileHeader';
import { SidebarProvider } from '@/contexts/SidebarContext';


interface DashboardLayoutProps {
  children: React.ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <SidebarProvider>
      <div className="flex h-screen overflow-hidden bg-[#f0f4f8] dark:bg-[#0c1929] text-neutral-900 dark:text-neutral-100">
        {/* Metropolis Background */}
        <div className="metropolis-sky">
          <div className="flying-hero" />
          <div className="hope-shine" />
        </div>

        {/* Desktop Sidebar */}
        <Sidebar />

        {/* Main Content Area */}
        <main className="flex-1 flex flex-col h-full overflow-hidden relative z-10">
          {/* Mobile Header */}
          <MobileHeader />

          {/* Scrollable Content */}
          <div className="flex-1 overflow-y-auto">
            <div className="p-4 md:p-6 lg:p-8 max-w-7xl mx-auto w-full">
              {children}
            </div>
          </div>
        </main>
      </div>
    </SidebarProvider>
  );
}
