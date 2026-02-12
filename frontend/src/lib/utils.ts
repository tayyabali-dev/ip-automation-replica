import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// Helper function to format file size with appropriate units
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  
  if (bytes < 1024) {
    return `${bytes} Bytes`;
  }
  
  if (bytes < 1024 * 1024) {
    // Less than 1 MB - show in KB
    const kb = bytes / 1024;
    return `${kb.toFixed(1)} KB`;
  }
  
  // 1 MB or larger - show in MB
  const mb = bytes / (1024 * 1024);
  return `${mb.toFixed(1)} MB`;
}