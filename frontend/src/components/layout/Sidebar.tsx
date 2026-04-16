'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ChevronLeft, ChevronRight, LogOut, User, Moon, Sun, Sparkles } from 'lucide-react';
import { useSidebar } from '@/contexts/SidebarContext';
import { useAuth } from '@/contexts/AuthContext';
import { useTheme } from '@/contexts/ThemeContext';
import { navigationItems, bottomNavItems } from '@/config/navigation';
import { OmnitrixLogo } from '@/components/ui/OmnitrixLogo';
import { cn } from '@/lib/utils';

export function Sidebar() {
  const pathname = usePathname();
  const { isCollapsed, toggleCollapsed } = useSidebar();
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();

  const isActive = (href: string) => {
    if (href === '/dashboard') {
      return pathname === '/dashboard';
    }
    return pathname.startsWith(href);
  };

  return (
    <aside
      className={cn(
        "hidden md:flex flex-col bg-[#0f172a]/95 backdrop-blur-xl border-r border-primary-500/20 h-full flex-shrink-0 z-20 transition-all duration-300 ease-in-out",
        isCollapsed ? "w-20" : "w-72"
      )}
    >
      {/* Logo Area */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-primary-500/20">
        <Link href="/dashboard" className="flex items-center gap-3 overflow-hidden">
          <div className="w-10 h-10 rounded-xl bg-primary-500/10 border border-primary-500/30 flex items-center justify-center flex-shrink-0">
            <OmnitrixLogo size={24} className="text-primary-500" />
          </div>
          <span
            className={cn(
              "text-sm font-bold text-primary-500 tracking-[0.2em] uppercase transition-opacity duration-200 whitespace-nowrap text-glow-omni",
              isCollapsed ? "opacity-0 w-0" : "opacity-100"
            )}
          >
            Omnitrix IP
          </span>
        </Link>
        <button
          onClick={toggleCollapsed}
          className={cn(
            "p-1.5 rounded-lg hover:bg-primary-500/10 text-neutral-500 hover:text-primary-500 transition-all",
            isCollapsed && "absolute right-2"
          )}
        >
          {isCollapsed ? (
            <ChevronRight className="w-4 h-4" />
          ) : (
            <ChevronLeft className="w-4 h-4" />
          )}
        </button>
      </div>

      {/* Main Navigation */}
      <nav className="flex-1 py-4 px-3 overflow-y-auto">
        {/* Section Label */}
        {!isCollapsed && (
          <p className="px-3 mb-2 text-[10px] font-bold uppercase tracking-[0.3em] text-primary-500/50">
            Missions
          </p>
        )}
        <ul className="space-y-1">
          {navigationItems.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.href);

            return (
              <li key={item.key} className="relative group">
                <Link
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200",
                    active
                      ? "bg-primary-500/15 border border-primary-500/30 text-primary-500"
                      : "text-neutral-400 hover:bg-primary-500/10 hover:text-primary-500 border border-transparent"
                  )}
                >
                  <Icon className={cn("w-[18px] h-[18px] flex-shrink-0", active ? "text-primary-500 drop-shadow-[0_0_8px_rgba(16,185,129,0.6)]" : "text-neutral-500")} />
                  <span
                    className={cn(
                      "text-[13px] font-medium tracking-wide transition-opacity duration-200 whitespace-nowrap",
                      active && "font-semibold",
                      isCollapsed ? "opacity-0 w-0" : "opacity-100"
                    )}
                  >
                    {item.label}
                  </span>
                </Link>
                {/* Tooltip for collapsed state */}
                {isCollapsed && (
                  <div className="absolute left-full top-1/2 -translate-y-1/2 ml-2 px-3 py-1.5 bg-[#0f172a] border border-primary-500/30 text-primary-500 text-[13px] font-medium rounded-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 whitespace-nowrap z-50 shadow-lg">
                    {item.label}
                  </div>
                )}
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Bottom Navigation */}
      <div className="py-4 px-3 border-t border-primary-500/20">
        {/* Section Label */}
        {!isCollapsed && (
          <p className="px-3 mb-2 text-[10px] font-bold uppercase tracking-[0.3em] text-primary-500/50">
            System
          </p>
        )}
        <ul className="space-y-1">
          {bottomNavItems.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.href);

            return (
              <li key={item.key} className="relative group">
                <Link
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200",
                    active
                      ? "bg-primary-500/15 border border-primary-500/30 text-primary-500"
                      : "text-neutral-400 hover:bg-primary-500/10 hover:text-primary-500 border border-transparent"
                  )}
                >
                  <Icon className={cn("w-[18px] h-[18px] flex-shrink-0", active ? "text-primary-500 drop-shadow-[0_0_8px_rgba(16,185,129,0.6)]" : "text-neutral-500")} />
                  <span
                    className={cn(
                      "text-[13px] font-medium tracking-wide transition-opacity duration-200 whitespace-nowrap",
                      active && "font-semibold",
                      isCollapsed ? "opacity-0 w-0" : "opacity-100"
                    )}
                  >
                    {item.label}
                  </span>
                </Link>
                {isCollapsed && (
                  <div className="absolute left-full top-1/2 -translate-y-1/2 ml-2 px-3 py-1.5 bg-[#0f172a] border border-primary-500/30 text-primary-500 text-[13px] font-medium rounded-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 whitespace-nowrap z-50 shadow-lg">
                    {item.label}
                  </div>
                )}
              </li>
            );
          })}

          {/* Theme Toggle */}
          <li className="relative group">
            <button
              onClick={toggleTheme}
              className="flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 text-neutral-400 hover:bg-primary-500/10 hover:text-primary-500 w-full border border-transparent"
            >
              {theme === 'dark' ? (
                <Sun className="w-[18px] h-[18px] flex-shrink-0 text-neutral-500" />
              ) : (
                <Moon className="w-[18px] h-[18px] flex-shrink-0 text-neutral-500" />
              )}
              <span
                className={cn(
                  "text-[13px] font-medium tracking-wide transition-opacity duration-200 whitespace-nowrap",
                  isCollapsed ? "opacity-0 w-0" : "opacity-100"
                )}
              >
                {theme === 'dark' ? 'Day Mode' : 'Night Mode'}
              </span>
            </button>
            {isCollapsed && (
              <div className="absolute left-full top-1/2 -translate-y-1/2 ml-2 px-3 py-1.5 bg-[#0f172a] border border-primary-500/30 text-primary-500 text-[13px] font-medium rounded-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 whitespace-nowrap z-50 shadow-lg">
                {theme === 'dark' ? 'Day Mode' : 'Night Mode'}
              </div>
            )}
          </li>
        </ul>
      </div>

      {/* User Profile Section */}
      <div className="border-t border-primary-500/20 p-3">
        <div
          className={cn(
            "flex items-center gap-3 p-2 rounded-xl hover:bg-primary-500/10 transition-colors",
            isCollapsed ? "justify-center" : ""
          )}
        >
          <div className="w-9 h-9 rounded-full bg-primary-500/10 border border-primary-500/30 flex items-center justify-center flex-shrink-0">
            <Sparkles className="w-4 h-4 text-primary-500" />
          </div>
          {!isCollapsed && (
            <div className="flex-1 min-w-0">
              <p className="text-[13px] font-semibold text-neutral-100 truncate leading-tight">
                {user?.full_name || 'Wielder'}
              </p>
              <p className="text-[11px] text-neutral-400 truncate leading-tight mt-0.5">
                {user?.email || 'ben@omnitrix.com'}
              </p>
            </div>
          )}
          <button
            onClick={logout}
            className={cn(
              "p-2 rounded-lg hover:bg-red-500/10 text-neutral-500 hover:text-red-400 transition-all",
              isCollapsed && "hidden"
            )}
            title="Sign Out"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
}
