'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Menu, X, LogOut, User } from 'lucide-react';
import { useSidebar } from '@/contexts/SidebarContext';
import { useAuth } from '@/contexts/AuthContext';
import { navigationItems, bottomNavItems } from '@/config/navigation';
import { cn } from '@/lib/utils';

export function MobileHeader() {
  const pathname = usePathname();
  const { isMobileOpen, toggleMobile, closeMobile } = useSidebar();
  const { user, logout } = useAuth();

  const isActive = (href: string) => {
    if (href === '/dashboard') {
      return pathname === '/dashboard';
    }
    return pathname.startsWith(href);
  };

  return (
    <>
      {/* Mobile Header */}
      <header className="md:hidden flex items-center justify-between h-16 px-4 bg-white border-b border-neutral-200">
        <Link href="/dashboard" className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-primary-500 flex items-center justify-center">
            <span className="text-white font-bold">J</span>
          </div>
          <span className="text-base font-semibold text-neutral-900 tracking-tight">JWHD IP</span>
        </Link>
        <button
          onClick={toggleMobile}
          className="p-2 rounded-lg hover:bg-neutral-100 text-neutral-600 transition-colors"
        >
          {isMobileOpen ? (
            <X className="w-5 h-5" />
          ) : (
            <Menu className="w-5 h-5" />
          )}
        </button>
      </header>

      {/* Mobile Overlay */}
      {isMobileOpen && (
        <div
          className="md:hidden fixed inset-0 bg-black/20 backdrop-blur-sm z-40"
          onClick={closeMobile}
        />
      )}

      {/* Mobile Sidebar */}
      <aside
        className={cn(
          "md:hidden fixed top-0 left-0 h-full w-72 bg-white z-50 transform transition-transform duration-300 ease-in-out shadow-xl",
          isMobileOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        {/* Logo Area */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-neutral-100">
          <Link href="/dashboard" className="flex items-center gap-3" onClick={closeMobile}>
            <div className="w-9 h-9 rounded-xl bg-primary-500 flex items-center justify-center">
              <span className="text-white font-bold">J</span>
            </div>
            <span className="text-base font-semibold text-neutral-900 tracking-tight">JWHD IP</span>
          </Link>
          <button
            onClick={closeMobile}
            className="p-2 rounded-lg hover:bg-neutral-100 text-neutral-400"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 py-4 px-3 overflow-y-auto">
          {/* Section Label */}
          <p className="px-3 mb-2 text-[11px] font-semibold uppercase tracking-wider text-neutral-400">
            Menu
          </p>
          <ul className="space-y-1">
            {navigationItems.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.href);

              return (
                <li key={item.key}>
                  <Link
                    href={item.href}
                    onClick={closeMobile}
                    className={cn(
                      "flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200",
                      active
                        ? "bg-neutral-100 text-neutral-900"
                        : "text-neutral-500 hover:bg-neutral-50 hover:text-neutral-900"
                    )}
                  >
                    <Icon className={cn("w-[18px] h-[18px]", active ? "text-primary-500" : "text-neutral-400")} />
                    <span className={cn(
                      "text-[13px] font-medium tracking-[-0.01em]",
                      active && "font-semibold"
                    )}>
                      {item.label}
                    </span>
                  </Link>
                </li>
              );
            })}
          </ul>

          {/* Support Section */}
          <div className="mt-6 pt-4 border-t border-neutral-100">
            <p className="px-3 mb-2 text-[11px] font-semibold uppercase tracking-wider text-neutral-400">
              Support
            </p>
            <ul className="space-y-1">
              {bottomNavItems.map((item) => {
                const Icon = item.icon;
                const active = isActive(item.href);

                return (
                  <li key={item.key}>
                    <Link
                      href={item.href}
                      onClick={closeMobile}
                      className={cn(
                        "flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200",
                        active
                          ? "bg-neutral-100 text-neutral-900"
                          : "text-neutral-500 hover:bg-neutral-50 hover:text-neutral-900"
                      )}
                    >
                      <Icon className={cn("w-[18px] h-[18px]", active ? "text-primary-500" : "text-neutral-400")} />
                      <span className={cn(
                        "text-[13px] font-medium tracking-[-0.01em]",
                        active && "font-semibold"
                      )}>
                        {item.label}
                      </span>
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
        </nav>

        {/* User Section */}
        <div className="border-t border-neutral-100 p-3">
          <div className="flex items-center gap-3 p-2 rounded-xl hover:bg-neutral-50 transition-colors">
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-primary-100 to-primary-50 flex items-center justify-center ring-2 ring-white shadow-sm">
              <User className="w-4 h-4 text-primary-600" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-[13px] font-semibold text-neutral-900 truncate leading-tight">
                {user?.full_name || 'User'}
              </p>
              <p className="text-[11px] text-neutral-500 truncate leading-tight mt-0.5">
                {user?.email || ''}
              </p>
            </div>
            <button
              onClick={() => {
                closeMobile();
                logout();
              }}
              className="p-2 rounded-lg hover:bg-red-50 text-neutral-400 hover:text-red-500 transition-all"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </aside>
    </>
  );
}
