'use client';

import React from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { User, Mail, Building, LogOut } from 'lucide-react';

export default function SettingsPage() {
  const { user, logout } = useAuth();

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl md:text-3xl font-semibold tracking-tight text-neutral-900 dark:text-neutral-100">
          Settings
        </h1>
        <p className="text-neutral-500 dark:text-neutral-400 mt-1">
          Manage your account and preferences
        </p>
      </div>

      {/* Profile Card */}
      <Card>
        <CardHeader>
          <CardTitle>Profile Information</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-4 p-4 rounded-xl bg-neutral-50 dark:bg-neutral-800">
            <div className="w-14 h-14 rounded-full bg-gradient-to-br from-primary-100 to-primary-50 dark:from-primary-900 dark:to-primary-800 flex items-center justify-center ring-4 ring-white dark:ring-neutral-900 shadow-sm">
              <User className="w-6 h-6 text-primary-600 dark:text-primary-400" />
            </div>
            <div>
              <p className="font-semibold text-neutral-900 dark:text-neutral-100">
                {user?.full_name || 'User'}
              </p>
              <p className="text-sm text-neutral-500 dark:text-neutral-400">
                {user?.email || 'No email'}
              </p>
            </div>
          </div>

          <div className="grid gap-4 pt-2">
            <div className="flex items-center gap-3 p-3 rounded-lg border border-neutral-100 dark:border-neutral-800">
              <Mail className="w-5 h-5 text-neutral-400 dark:text-neutral-500" />
              <div>
                <p className="text-xs text-neutral-500 dark:text-neutral-400">Email</p>
                <p className="text-sm font-medium text-neutral-900 dark:text-neutral-100">
                  {user?.email || 'Not set'}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 rounded-lg border border-neutral-100 dark:border-neutral-800">
              <Building className="w-5 h-5 text-neutral-400 dark:text-neutral-500" />
              <div>
                <p className="text-xs text-neutral-500 dark:text-neutral-400">Organization</p>
                <p className="text-sm font-medium text-neutral-900 dark:text-neutral-100">
                  JWHD IP
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Account Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Account</CardTitle>
        </CardHeader>
        <CardContent>
          <Button
            variant="outline"
            onClick={logout}
            className="text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 hover:bg-red-50 dark:hover:bg-red-950 hover:border-red-200 dark:hover:border-red-800"
          >
            <LogOut className="w-4 h-4 mr-2" />
            Sign Out
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}

