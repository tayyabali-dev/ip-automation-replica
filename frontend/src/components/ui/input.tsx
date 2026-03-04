'use client';

import * as React from "react"
import { cn } from "@/lib/utils"

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          "flex h-11 w-full rounded-lg border border-neutral-200 dark:border-neutral-700 bg-white/50 dark:bg-neutral-800/50 px-4 py-2.5 text-sm text-neutral-900 dark:text-neutral-100 transition-all duration-200 file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-neutral-400 dark:placeholder:text-neutral-500 focus:border-primary-500 focus:ring-2 focus:ring-primary-500/10 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50 disabled:bg-neutral-50 dark:disabled:bg-neutral-800",
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
Input.displayName = "Input"

export { Input }

