'use client';

import * as React from "react"
import { cn } from "@/lib/utils"

interface ProgressCircleProps {
  value: number
  size?: number
  strokeWidth?: number
  className?: string
  showValue?: boolean
  color?: 'primary' | 'success' | 'warning' | 'danger'
  label?: string
}

const colorMap = {
  primary: 'stroke-primary-500',
  success: 'stroke-emerald-500',
  warning: 'stroke-amber-500',
  danger: 'stroke-red-500',
}

const bgColorMap = {
  primary: 'stroke-primary-100 dark:stroke-primary-900',
  success: 'stroke-emerald-100 dark:stroke-emerald-900',
  warning: 'stroke-amber-100 dark:stroke-amber-900',
  danger: 'stroke-red-100 dark:stroke-red-900',
}

export function ProgressCircle({
  value,
  size = 120,
  strokeWidth = 10,
  className,
  showValue = true,
  color = 'primary',
  label,
}: ProgressCircleProps) {
  const radius = (size - strokeWidth) / 2
  const circumference = radius * 2 * Math.PI
  const offset = circumference - (value / 100) * circumference

  return (
    <div className={cn("relative inline-flex items-center justify-center", className)}>
      <svg
        width={size}
        height={size}
        className="transform -rotate-90"
      >
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          strokeWidth={strokeWidth}
          className={cn("transition-all duration-300", bgColorMap[color])}
        />
        {/* Progress circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className={cn(
            "transition-all duration-700 ease-out",
            colorMap[color]
          )}
        />
      </svg>
      {showValue && (
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-2xl font-semibold text-neutral-900 dark:text-neutral-100">
            {Math.round(value)}%
          </span>
          {label && (
            <span className="text-xs text-neutral-500 dark:text-neutral-400 mt-0.5">{label}</span>
          )}
        </div>
      )}
    </div>
  )
}

export { ProgressCircle as default }

