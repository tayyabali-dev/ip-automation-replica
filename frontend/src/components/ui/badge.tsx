'use client';

import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium transition-colors",
  {
    variants: {
      variant: {
        default: "bg-neutral-100 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300",
        primary: "bg-primary-100 dark:bg-primary-900/50 text-primary-700 dark:text-primary-300",
        success: "bg-emerald-100 dark:bg-emerald-900/50 text-emerald-700 dark:text-emerald-300",
        warning: "bg-amber-100 dark:bg-amber-900/50 text-amber-700 dark:text-amber-300",
        danger: "bg-red-100 dark:bg-red-900/50 text-red-700 dark:text-red-300",
        info: "bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300",
        outline: "border border-neutral-200 dark:border-neutral-700 text-neutral-700 dark:text-neutral-300 bg-transparent",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  )
}

export { Badge, badgeVariants }

