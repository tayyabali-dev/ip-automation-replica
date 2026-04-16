'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { useAuth } from '@/contexts/AuthContext';
import { useTheme } from '@/contexts/ThemeContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { OmnitrixLogo } from '@/components/ui/OmnitrixLogo';
import api from '@/lib/axios';
import { ArrowRight, Zap } from 'lucide-react';

export default function LoginPage() {
  const { register, handleSubmit, formState: { errors } } = useForm();
  const { login } = useAuth();
  const { theme, toggleTheme } = useTheme();
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
      setError(err.response?.data?.detail || 'Access denied. The Omnitrix rejected your DNA.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen overflow-x-hidden selection:bg-primary-500/20 selection:text-primary-500 relative text-neutral-200 flex items-center justify-center p-4">
      {/* Omnitrix Background */}
      <div className="omnitrix-bg">
        <div className="energy-grid" />
        <div className="omni-glow" />
      </div>

      {/* Background Elements */}
      <div className="fixed inset-0 pointer-events-none z-[1]">
        <div
          className="absolute inset-0 bg-grid-pattern"
          style={{
            maskImage: 'radial-gradient(ellipse at center, black 30%, transparent 80%)',
            WebkitMaskImage: 'radial-gradient(ellipse at center, black 30%, transparent 80%)',
          }}
        />
      </div>

      {/* Main Container */}
      <main className="relative z-10 w-full max-w-[420px]">
        {/* Logo Header */}
        <div className="flex justify-center mb-8 animate-fade-in">
          <div className="flex flex-col items-center gap-3">
            <div className="relative">
              <OmnitrixLogo size={56} className="text-primary-500 drop-shadow-[0_0_20px_rgba(16,185,129,0.7)]" />
              <div className="absolute inset-0 rounded-full bg-primary-500/10 blur-xl scale-150" />
            </div>
            <div className="text-center">
              <span className="text-xl font-bold tracking-[0.3em] uppercase text-primary-500 text-glow-omni">
                Omnitrix IP
              </span>
              <p className="text-[10px] tracking-[0.5em] uppercase text-neutral-500 mt-1">
                Tennyson Patents
              </p>
            </div>
          </div>
        </div>

        {/* Login Card */}
        <div className="relative bg-[#0f172a]/95 backdrop-blur-xl border border-primary-500/20 rounded-2xl p-8 md:p-10 shadow-2xl shadow-black/80 animate-slide-up border-glow">
          <div className="absolute top-0 left-0 w-8 h-8 border-t-2 border-l-2 border-primary-500/50 rounded-tl-2xl" />
          <div className="absolute top-0 right-0 w-8 h-8 border-t-2 border-r-2 border-primary-500/50 rounded-tr-2xl" />
          <div className="absolute bottom-0 left-0 w-8 h-8 border-b-2 border-l-2 border-primary-500/30 rounded-bl-2xl" />
          <div className="absolute bottom-0 right-0 w-8 h-8 border-b-2 border-r-2 border-primary-500/30 rounded-br-2xl" />

          <div className="text-center space-y-3 mb-8">
            <h1 className="text-xl font-medium tracking-tight text-white">
              Access Omnitrix
            </h1>
            <p className="text-sm text-neutral-400 font-serif italic text-balance leading-relaxed">
              &quot;It's Hero Time!&quot;
            </p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="space-y-1.5">
              <label htmlFor="email" className="block text-xs font-medium text-primary-500 uppercase tracking-wider">
                Wielder ID
              </label>
              <input
                type="email"
                id="email"
                placeholder="ben@omnitrix.com"
                className="block w-full rounded-lg border border-primary-500/25 bg-black/60 px-3 py-2.5 text-sm text-white placeholder:text-neutral-600 focus:border-primary-500/60 focus:ring-2 focus:ring-primary-500/25 focus:outline-none transition-all"
                {...register('email', { required: 'Wielder ID is required' })}
              />
              {errors.email && (
                <p className="text-xs text-red-400 mt-1">{errors.email.message as string}</p>
              )}
            </div>

            <div className="space-y-1.5">
              <label htmlFor="password" className="block text-xs font-medium text-primary-500 uppercase tracking-wider">
                DNA Code
              </label>
              <input
                type="password"
                id="password"
                placeholder="••••••••"
                className="block w-full rounded-lg border border-primary-500/25 bg-black/60 px-3 py-2.5 text-sm text-white placeholder:text-neutral-600 focus:border-primary-500/60 focus:ring-2 focus:ring-primary-500/25 focus:outline-none transition-all"
                {...register('password', { required: 'DNA code is required' })}
              />
              {errors.password && (
                <p className="text-xs text-red-400 mt-1">{errors.password.message as string}</p>
              )}
            </div>

            <div className="flex items-center justify-end">
              <a href="#" className="text-xs font-medium text-neutral-500 hover:text-primary-500 transition-colors">
                Forgot your DNA code?
              </a>
            </div>

            {error && (
              <div className="p-3 text-sm text-red-400 bg-red-500/10 rounded-lg border border-red-500/20">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="w-full group flex items-center justify-center gap-2 bg-primary-500 hover:bg-primary-600 text-black h-11 rounded-lg transition-all duration-300 font-bold text-sm shadow-[0_0_20px_rgba(16,185,129,0.5)] disabled:opacity-50 disabled:cursor-not-allowed uppercase tracking-wider hover:shadow-[0_0_30px_rgba(16,185,129,0.7)]"
            >
              {isLoading ? (
                <span className="flex items-center gap-2">
                  <Zap className="w-4 h-4 animate-pulse" />
                  Scanning DNA...
                </span>
              ) : (
                <>
                  Go Hero
                  <ArrowRight className="w-4 h-4 opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-300" />
                </>
              )}
            </button>
          </form>
        </div>

        <p className="mt-8 text-center text-xs text-neutral-600">
          ⌚ Omnitrix IP Division — It Started When An Alien Device Did What It Did
        </p>
      </main>
    </div>
  );
}
