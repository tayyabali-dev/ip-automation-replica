'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import api from '@/lib/axios';
import { ArrowRight } from 'lucide-react';

export default function LoginPage() {
  const { register, handleSubmit, formState: { errors } } = useForm();
  const { login } = useAuth();
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const onSubmit = async (data: any) => {
    setIsLoading(true);
    setError('');

    const formData = new FormData();
    formData.append('username', data.email);
    formData.append('password', data.password);

    try {
      const response = await api.post('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });

      login(response.data.access_token, response.data.user, response.data.refresh_token);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to login. Please check your credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen overflow-x-hidden selection:bg-primary-500/10 selection:text-primary-500 relative bg-neutral-50 text-neutral-900 flex items-center justify-center p-4">
      {/* Background Elements */}
      <div className="fixed inset-0 pointer-events-none z-0">
        {/* Grid Pattern */}
        <div
          className="absolute inset-0 bg-grid-pattern"
          style={{
            maskImage: 'radial-gradient(ellipse at center, black 40%, transparent 100%)',
            WebkitMaskImage: 'radial-gradient(ellipse at center, black 40%, transparent 100%)',
          }}
        />

        {/* Orange Glow */}
        <div className="absolute top-[-20%] left-1/2 -translate-x-1/2 w-[800px] h-[500px] rounded-[100%] bg-primary-500/5 blur-[120px]" />
      </div>

      {/* Main Container */}
      <main className="relative z-10 w-full max-w-[420px]">
        {/* Logo Header */}
        <div className="flex justify-center mb-8 animate-fade-in">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 bg-primary-500 rounded-xl text-white flex items-center justify-center font-bold text-xl tracking-tighter shadow-lg shadow-primary-500/20">
              J
            </div>
            <span className="text-xl font-semibold tracking-tight text-neutral-900">
              JWHD IP
            </span>
          </div>
        </div>

        {/* Login Card */}
        <div className="glass-panel-strong rounded-2xl p-8 md:p-10 shadow-xl shadow-black/[0.02] animate-slide-up">
          {/* Header Text */}
          <div className="text-center space-y-3 mb-8">
            <h1 className="text-xl font-medium tracking-tight text-neutral-900">
              Patent Application Automation
            </h1>
            <p className="text-sm text-neutral-500 font-serif italic text-balance leading-relaxed">
              "Streamline your USPTO filings with AI-powered automation"
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="space-y-1.5">
              <label htmlFor="email" className="block text-xs font-medium text-neutral-700">
                Email address
              </label>
              <Input
                type="email"
                id="email"
                placeholder="user@jwhd.com"
                {...register('email', { required: 'Email is required' })}
              />
              {errors.email && (
                <p className="text-xs text-red-500 mt-1">{errors.email.message as string}</p>
              )}
            </div>

            <div className="space-y-1.5">
              <label htmlFor="password" className="block text-xs font-medium text-neutral-700">
                Password
              </label>
              <Input
                type="password"
                id="password"
                {...register('password', { required: 'Password is required' })}
              />
              {errors.password && (
                <p className="text-xs text-red-500 mt-1">{errors.password.message as string}</p>
              )}
            </div>

            <div className="flex items-center justify-end">
              <a href="#" className="text-xs font-medium text-neutral-500 hover:text-primary-500 transition-colors">
                Forgot password?
              </a>
            </div>

            {error && (
              <div className="p-3 text-sm text-red-600 bg-red-50 rounded-lg border border-red-100">
                {error}
              </div>
            )}

            <Button
              type="submit"
              className="w-full group"
              disabled={isLoading}
            >
              {isLoading ? (
                'Signing in...'
              ) : (
                <>
                  Sign In
                  <ArrowRight className="w-4 h-4 opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-300" />
                </>
              )}
            </Button>
          </form>
        </div>

        {/* Footer */}
        <p className="mt-8 text-center text-xs text-neutral-400">
          JWHD IP Automation Platform
        </p>
      </main>
    </div>
  );
}
