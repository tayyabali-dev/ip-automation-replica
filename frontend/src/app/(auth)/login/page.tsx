'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { useAuth } from '@/contexts/AuthContext';
import { useTheme } from '@/contexts/ThemeContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { PokeballLogo } from '@/components/ui/PokeballLogo';
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
      setError(err.response?.data?.detail || 'Access denied. Not a registered Trainer.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen overflow-x-hidden selection:bg-primary-500/20 selection:text-primary-500 relative text-neutral-800 dark:text-neutral-100 flex items-center justify-center p-4">
      {/* Pokemon Background */}
      <div className="pokeball-pattern">
        <div className="floating-pokeballs" />
        <div className="sparkles" />
      </div>

      {/* Background Elements */}
      <div className="fixed inset-0 pointer-events-none z-[1]">
        {/* Pokedex grid */}
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
              <PokeballLogo size={56} className="text-primary-500 dark:text-primary-400 drop-shadow-[0_0_15px_rgba(220,10,45,0.4)]" />
              {/* Glow ring */}
              <div className="absolute inset-0 rounded-full bg-primary-500/10 blur-xl scale-150" />
            </div>
            <div className="text-center">
              <span className="text-xl font-bold tracking-[0.3em] uppercase text-primary-500 text-glow-red">
                PokePatent
              </span>
              <p className="text-[10px] tracking-[0.5em] uppercase text-neutral-500 dark:text-neutral-400 mt-1">
                Trainer Bureau
              </p>
            </div>
          </div>
        </div>

        {/* Login Card */}
        <div className="relative bg-white/95 dark:bg-[#1e293b]/95 backdrop-blur-xl border border-primary-500/15 rounded-2xl p-8 md:p-10 shadow-2xl shadow-primary-500/10 animate-slide-up border-glow">
          {/* Corner accents - Pokeball style */}
          <div className="absolute top-0 left-0 w-8 h-8 border-t-2 border-l-2 border-primary-500/40 rounded-tl-2xl" />
          <div className="absolute top-0 right-0 w-8 h-8 border-t-2 border-r-2 border-primary-500/40 rounded-tr-2xl" />
          <div className="absolute bottom-0 left-0 w-8 h-8 border-b-2 border-l-2 border-pokemon-yellow/40 rounded-bl-2xl" />
          <div className="absolute bottom-0 right-0 w-8 h-8 border-b-2 border-r-2 border-pokemon-yellow/40 rounded-br-2xl" />

          {/* Header Text */}
          <div className="text-center space-y-3 mb-8">
            <h1 className="text-xl font-medium tracking-tight text-neutral-900 dark:text-white">
              Trainer Login
            </h1>
            <p className="text-sm text-neutral-600 dark:text-neutral-400 font-serif italic text-balance leading-relaxed">
              &quot;Gotta patent 'em all!&quot;
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="space-y-1.5">
              <label htmlFor="email" className="block text-xs font-medium text-primary-500 uppercase tracking-wider">
                Trainer ID
              </label>
              <input
                type="email"
                id="email"
                placeholder="ash@pokepatent.com"
                className="block w-full rounded-lg border border-primary-500/20 bg-white dark:bg-black/40 px-3 py-2.5 text-sm text-neutral-900 dark:text-white placeholder:text-neutral-400 dark:placeholder:text-neutral-600 focus:border-primary-500/50 focus:ring-2 focus:ring-primary-500/20 focus:outline-none transition-all"
                {...register('email', { required: 'Trainer ID is required' })}
              />
              {errors.email && (
                <p className="text-xs text-red-400 mt-1">{errors.email.message as string}</p>
              )}
            </div>

            <div className="space-y-1.5">
              <label htmlFor="password" className="block text-xs font-medium text-primary-500 uppercase tracking-wider">
                Trainer Code
              </label>
              <input
                type="password"
                id="password"
                placeholder="••••••••"
                className="block w-full rounded-lg border border-primary-500/20 bg-white dark:bg-black/40 px-3 py-2.5 text-sm text-neutral-900 dark:text-white placeholder:text-neutral-400 dark:placeholder:text-neutral-600 focus:border-primary-500/50 focus:ring-2 focus:ring-primary-500/20 focus:outline-none transition-all"
                {...register('password', { required: 'Trainer code is required' })}
              />
              {errors.password && (
                <p className="text-xs text-red-400 mt-1">{errors.password.message as string}</p>
              )}
            </div>

            <div className="flex items-center justify-end">
              <a href="#" className="text-xs font-medium text-neutral-500 dark:text-neutral-400 hover:text-primary-500 transition-colors">
                Forgot your Trainer Code?
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
              className="w-full group flex items-center justify-center gap-2 bg-primary-500 hover:bg-primary-600 text-white h-11 rounded-lg transition-all duration-300 font-bold text-sm shadow-lg shadow-primary-500/30 disabled:opacity-50 disabled:cursor-not-allowed uppercase tracking-wider hover:shadow-primary-500/50"
            >
              {isLoading ? (
                <span className="flex items-center gap-2">
                  <Zap className="w-4 h-4 animate-pulse" />
                  Connecting to Pokedex...
                </span>
              ) : (
                <>
                  Begin Journey
                  <ArrowRight className="w-4 h-4 opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-300" />
                </>
              )}
            </button>
          </form>
        </div>

        {/* Footer */}
        <p className="mt-8 text-center text-xs text-neutral-500 dark:text-neutral-600">
          ⚡ PokePatent Bureau — Where Innovation Meets Evolution
        </p>
      </main>
    </div>
  );
}
