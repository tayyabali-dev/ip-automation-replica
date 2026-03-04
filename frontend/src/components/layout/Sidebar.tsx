'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ChevronLeft, ChevronRight, LogOut, User, Moon, Sun } from 'lucide-react';
import { useSidebar } from '@/contexts/SidebarContext';
import { useAuth } from '@/contexts/AuthContext';
import { useTheme } from '@/contexts/ThemeContext';
import { navigationItems, bottomNavItems } from '@/config/navigation';
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
        "hidden md:flex flex-col bg-white dark:bg-neutral-900 border-r border-neutral-200 dark:border-neutral-800 h-full flex-shrink-0 z-20 transition-all duration-300 ease-in-out",
        isCollapsed ? "w-20" : "w-72"
      )}
    >
      {/* Logo Area */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-neutral-100 dark:border-neutral-800">
        <Link href="/dashboard" className="flex items-center gap-3 overflow-hidden">
          <div className="w-10 h-10 rounded-xl bg-primary-500 flex items-center justify-center flex-shrink-0">
            <span className="text-white font-bold text-lg">J</span>
          </div>
          <span
            className={cn(
              "text-base font-semibold text-neutral-900 dark:text-neutral-100 tracking-tight transition-opacity duration-200 whitespace-nowrap",
              isCollapsed ? "opacity-0 w-0" : "opacity-100"
            )}
          >
            JWHD IP
          </span>
        </Link>
        <button
          onClick={toggleCollapsed}
          className={cn(
            "p-1.5 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-800 text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-300 transition-all",
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
          <p className="px-3 mb-2 text-[11px] font-semibold uppercase tracking-wider text-neutral-400 dark:text-neutral-500">
            Menu
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
                      ? "bg-neutral-100 dark:bg-neutral-800 text-neutral-900 dark:text-neutral-100"
                      : "text-neutral-500 dark:text-neutral-400 hover:bg-neutral-50 dark:hover:bg-neutral-800/50 hover:text-neutral-900 dark:hover:text-neutral-200"
                  )}
                >
                  <Icon className={cn("w-[18px] h-[18px] flex-shrink-0", active ? "text-primary-500" : "text-neutral-400 dark:text-neutral-500")} />
                  <span
                    className={cn(
                      "text-[13px] font-medium tracking-[-0.01em] transition-opacity duration-200 whitespace-nowrap",
                      active && "font-semibold",
                      isCollapsed ? "opacity-0 w-0" : "opacity-100"
                    )}
                  >
                    {item.label}
                  </span>
                </Link>
                {/* Tooltip for collapsed state */}
                {isCollapsed && (
                  <div className="absolute left-full top-1/2 -translate-y-1/2 ml-2 px-3 py-1.5 bg-neutral-900 dark:bg-neutral-100 text-white dark:text-neutral-900 text-[13px] font-medium rounded-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 whitespace-nowrap z-50 shadow-lg">
                    {item.label}
                  </div>
                )}
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Bottom Navigation */}
      <div className="py-4 px-3 border-t border-neutral-100 dark:border-neutral-800">
        {/* Section Label */}
        {!isCollapsed && (
          <p className="px-3 mb-2 text-[11px] font-semibold uppercase tracking-wider text-neutral-400 dark:text-neutral-500">
            Support
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
                      ? "bg-neutral-100 dark:bg-neutral-800 text-neutral-900 dark:text-neutral-100"
                      : "text-neutral-500 dark:text-neutral-400 hover:bg-neutral-50 dark:hover:bg-neutral-800/50 hover:text-neutral-900 dark:hover:text-neutral-200"
                  )}
                >
                  <Icon className={cn("w-[18px] h-[18px] flex-shrink-0", active ? "text-primary-500" : "text-neutral-400 dark:text-neutral-500")} />
                  <span
                    className={cn(
                      "text-[13px] font-medium tracking-[-0.01em] transition-opacity duration-200 whitespace-nowrap",
                      active && "font-semibold",
                      isCollapsed ? "opacity-0 w-0" : "opacity-100"
                    )}
                  >
                    {item.label}
                  </span>
                </Link>
                {isCollapsed && (
                  <div className="absolute left-full top-1/2 -translate-y-1/2 ml-2 px-3 py-1.5 bg-neutral-900 dark:bg-neutral-100 text-white dark:text-neutral-900 text-[13px] font-medium rounded-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 whitespace-nowrap z-50 shadow-lg">
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
              className="flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 text-neutral-500 dark:text-neutral-400 hover:bg-neutral-50 dark:hover:bg-neutral-800/50 hover:text-neutral-900 dark:hover:text-neutral-200 w-full"
            >
              {theme === 'dark' ? (
                <Sun className="w-[18px] h-[18px] flex-shrink-0 text-neutral-400 dark:text-neutral-500" />
              ) : (
                <Moon className="w-[18px] h-[18px] flex-shrink-0 text-neutral-400" />
              )}
              <span
                className={cn(
                  "text-[13px] font-medium tracking-[-0.01em] transition-opacity duration-200 whitespace-nowrap",
                  isCollapsed ? "opacity-0 w-0" : "opacity-100"
                )}
              >
                {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
              </span>
            </button>
            {isCollapsed && (
              <div className="absolute left-full top-1/2 -translate-y-1/2 ml-2 px-3 py-1.5 bg-neutral-900 dark:bg-neutral-100 text-white dark:text-neutral-900 text-[13px] font-medium rounded-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 whitespace-nowrap z-50 shadow-lg">
                {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
              </div>
            )}
          </li>
        </ul>
      </div>

      {/* User Profile Section */}
      <div className="border-t border-neutral-100 dark:border-neutral-800 p-3">
        <div
          className={cn(
            "flex items-center gap-3 p-2 rounded-xl hover:bg-neutral-50 dark:hover:bg-neutral-800 transition-colors",
            isCollapsed ? "justify-center" : ""
          )}
        >
          <div className="w-9 h-9 rounded-full bg-gradient-to-br from-primary-100 to-primary-50 dark:from-primary-900 dark:to-primary-800 flex items-center justify-center flex-shrink-0 ring-2 ring-white dark:ring-neutral-800 shadow-sm">
            <User className="w-4 h-4 text-primary-600 dark:text-primary-400" />
          </div>
          {!isCollapsed && (
            <div className="flex-1 min-w-0">
              <p className="text-[13px] font-semibold text-neutral-900 dark:text-neutral-100 truncate leading-tight">
                {user?.full_name || 'User'}
              </p>
              <p className="text-[11px] text-neutral-500 dark:text-neutral-400 truncate leading-tight mt-0.5">
                {user?.email || ''}
              </p>
            </div>
          )}
          <button
            onClick={logout}
            className={cn(
              "p-2 rounded-lg hover:bg-red-50 dark:hover:bg-red-950 text-neutral-400 hover:text-red-500 transition-all",
              isCollapsed && "hidden"
            )}
            title="Sign out"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
}

