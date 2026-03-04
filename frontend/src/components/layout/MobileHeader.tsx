'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Menu, X, LogOut, Sparkles, Moon, Sun } from 'lucide-react';
import { useSidebar } from '@/contexts/SidebarContext';
import { useAuth } from '@/contexts/AuthContext';
import { useTheme } from '@/contexts/ThemeContext';
import { navigationItems, bottomNavItems } from '@/config/navigation';
import { ImperialLogo } from '@/components/ui/ImperialLogo';
import { cn } from '@/lib/utils';

export function MobileHeader() {
  const pathname = usePathname();
  const { isMobileOpen, toggleMobile, closeMobile } = useSidebar();
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();

  const isActive = (href: string) => {
    if (href === '/dashboard') {
      return pathname === '/dashboard';
    }
    return pathname.startsWith(href);
  };

  return (
    <>
      {/* Mobile Header */}
      <header className="md:hidden flex items-center justify-between h-16 px-4 bg-[#0d0e14]/95 backdrop-blur-xl border-b border-primary-500/10">
        <Link href="/dashboard" className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-primary-500/10 border border-primary-500/20 flex items-center justify-center">
            <ImperialLogo size={20} className="text-primary-500" />
          </div>
          <span className="text-sm font-bold text-primary-500 tracking-[0.2em] uppercase text-glow-yellow">Galactic IP</span>
        </Link>
        <div className="flex items-center gap-2">
          <button
            onClick={toggleTheme}
            className="p-2 rounded-lg hover:bg-white/5 text-neutral-400 hover:text-primary-500 transition-colors"
          >
            {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          </button>
          <button
            onClick={toggleMobile}
            className="p-2 rounded-lg hover:bg-white/5 text-neutral-400 hover:text-primary-500 transition-colors"
          >
            {isMobileOpen ? (
              <X className="w-5 h-5" />
            ) : (
              <Menu className="w-5 h-5" />
            )}
          </button>
        </div>
      </header>

      {/* Mobile Overlay */}
      {isMobileOpen && (
        <div
          className="md:hidden fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
          onClick={closeMobile}
        />
      )}

      {/* Mobile Sidebar */}
      <aside
        className={cn(
          "md:hidden fixed top-0 left-0 h-full w-72 bg-[#0d0e14]/98 backdrop-blur-xl border-r border-primary-500/10 z-50 transform transition-transform duration-300 ease-in-out shadow-xl shadow-black/50",
          isMobileOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        {/* Logo Area */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-primary-500/10">
          <Link href="/dashboard" className="flex items-center gap-3" onClick={closeMobile}>
            <div className="w-9 h-9 rounded-xl bg-primary-500/10 border border-primary-500/20 flex items-center justify-center">
              <ImperialLogo size={20} className="text-primary-500" />
            </div>
            <span className="text-sm font-bold text-primary-500 tracking-[0.2em] uppercase text-glow-yellow">Galactic IP</span>
          </Link>
          <button
            onClick={closeMobile}
            className="p-2 rounded-lg hover:bg-white/5 text-neutral-500 hover:text-primary-500"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 py-4 px-3 overflow-y-auto">
          {/* Section Label */}
          <p className="px-3 mb-2 text-[10px] font-bold uppercase tracking-[0.3em] text-primary-500/40">
            Operations
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
                        ? "bg-primary-500/10 border border-primary-500/20 text-primary-500"
                        : "text-neutral-400 hover:bg-white/5 hover:text-primary-300 border border-transparent"
                    )}
                  >
                    <Icon className={cn("w-[18px] h-[18px]", active ? "text-primary-500 drop-shadow-[0_0_6px_rgba(255,232,31,0.5)]" : "text-neutral-500")} />
                    <span className={cn(
                      "text-[13px] font-medium tracking-wide",
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
          <div className="mt-6 pt-4 border-t border-primary-500/10">
            <p className="px-3 mb-2 text-[10px] font-bold uppercase tracking-[0.3em] text-primary-500/40">
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
                          ? "bg-primary-500/10 border border-primary-500/20 text-primary-500"
                          : "text-neutral-400 hover:bg-white/5 hover:text-primary-300 border border-transparent"
                      )}
                    >
                      <Icon className={cn("w-[18px] h-[18px]", active ? "text-primary-500 drop-shadow-[0_0_6px_rgba(255,232,31,0.5)]" : "text-neutral-500")} />
                      <span className={cn(
                        "text-[13px] font-medium tracking-wide",
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
        <div className="border-t border-primary-500/10 p-3">
          <div className="flex items-center gap-3 p-2 rounded-xl hover:bg-white/5 transition-colors">
            <div className="w-9 h-9 rounded-full bg-primary-500/10 border border-primary-500/20 flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-primary-500" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-[13px] font-semibold text-neutral-100 truncate leading-tight">
                {user?.full_name || 'Jedi Knight'}
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
              className="p-2 rounded-lg hover:bg-red-500/10 text-neutral-500 hover:text-red-400 transition-all"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </aside>
    </>
  );
}
