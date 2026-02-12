'use client';

import React, { useCallback, useState } from 'react';
import { Upload, FileText, AlertCircle, Loader2, X, Plus } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { cn, formatFileSize } from '@/lib/utils';
import { Button } from '@/components/ui/button';

interface FileWithStatus {
  file: File;
  status: 'pending' | 'processing' | 'completed' | 'error';
  progress: number;
  error?: string;
}

interface FileUploadProps {
  onFilesReady: (files: File[]) => void;
  isLoading?: boolean;
  uploadProgress?: number;
  error?: string | null;
  maxFiles?: number;
  isProcessing?: boolean;
  onError?: (error: string) => void;
}

const ACCEPTED_FILE_TYPES = [
  'application/pdf',
  'text/csv',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
];

export const FileUpload: React.FC<FileUploadProps> = ({
  onFilesReady,
  isLoading = false,
  uploadProgress = 0,
  error = null,
  maxFiles = 4,
  isProcessing = false,
  onError
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<FileWithStatus[]>([]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const addFiles = useCallback((newFiles: FileList | File[]) => {
    const filesArray = Array.from(newFiles);

    setSelectedFiles(currentFiles => {
      const validFiles = filesArray.filter(file =>
        ACCEPTED_FILE_TYPES.includes(file.type) &&
        !currentFiles.some(sf => sf.file.name === file.name)
      );

      if (currentFiles.length + validFiles.length > maxFiles) {
        const allowedCount = maxFiles - currentFiles.length;
        validFiles.splice(allowedCount);
      }

      const newFileStatuses: FileWithStatus[] = validFiles.map(file => ({
        file,
        status: 'pending',
        progress: 0
      }));

      return [...currentFiles, ...newFileStatuses];
    });
  }, [maxFiles]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    if (e.dataTransfer.files) {
      addFiles(e.dataTransfer.files);
    }
  }, [addFiles]);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      addFiles(e.target.files);
      e.target.value = '';
    }
  }, [addFiles]);

  const removeFile = useCallback((index: number) => {
    setSelectedFiles(currentFiles => currentFiles.filter((_, i) => i !== index));
  }, []);

  const canAddMore = selectedFiles.length < maxFiles;

  const handleProcessFiles = useCallback(() => {
    if (selectedFiles.length === 0) {
      const errorMessage = "Please select at least one file before starting extraction.";
      if (onError) {
        onError(errorMessage);
      }
      return;
    }

    if (onError) {
      onError('');
    }

    const files = selectedFiles.map(fs => fs.file);
    onFilesReady(files);
  }, [selectedFiles, onFilesReady, onError]);

  return (
    <div className="w-full max-w-xl mx-auto">
      <Card
        className={cn(
          "border-2 border-dashed transition-all duration-300 rounded-2xl",
          isDragging ? "border-primary-500 bg-primary-50/50" : "border-neutral-200 hover:border-neutral-300",
          error ? "border-red-400 bg-red-50/50" : ""
        )}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDragEnter={handleDragEnter}
        onDrop={handleDrop}
      >
        <CardContent className="flex flex-col items-center justify-center p-10 space-y-4">
          <div className="relative">
            {isLoading ? (
              <div className="h-16 w-16 flex items-center justify-center rounded-full bg-primary-100 animate-pulse">
                <Loader2 className="h-8 w-8 text-primary-500 animate-spin" />
              </div>
            ) : (
              <div className={cn(
                "h-16 w-16 flex items-center justify-center rounded-full transition-colors",
                error ? "bg-red-100" : isDragging ? "bg-primary-100" : "bg-neutral-100"
              )}>
                {error ? (
                  <AlertCircle className="h-8 w-8 text-red-500" />
                ) : (
                  <Upload className={cn(
                    "h-8 w-8 transition-colors",
                    isDragging ? "text-primary-500" : "text-neutral-400"
                  )} />
                )}
              </div>
            )}
          </div>

          <div className="text-center space-y-2 w-full max-w-sm">
            <h3 className="text-lg font-semibold text-neutral-900">
              {isLoading ? "Processing Documents..." : "Upload Your Documents"}
            </h3>

            <p className="text-sm text-neutral-500 max-w-xs mx-auto">
              {error || `Drag and drop up to ${maxFiles} files here, or click to browse`}
            </p>
          </div>

          {!isProcessing && canAddMore && (
            <div className="flex flex-col items-center gap-4 w-full">
              <input
                type="file"
                accept=".pdf,.csv,.docx"
                className="hidden"
                id="file-upload"
                onChange={handleFileInput}
                disabled={isLoading}
                multiple
              />
              <label htmlFor="file-upload">
                <Button variant="outline" className="cursor-pointer" asChild>
                  <span>
                    <Plus className="mr-2 h-4 w-4" />
                    {selectedFiles.length === 0 ? 'Select Files' : 'Add More Files'}
                  </span>
                </Button>
              </label>
            </div>
          )}

          {/* File Queue */}
          {selectedFiles.length > 0 && (
            <div className="w-full max-w-md space-y-3">
              <h4 className="text-sm font-medium text-neutral-700 text-center">
                Selected Files ({selectedFiles.length}/{maxFiles})
              </h4>
              <div className="space-y-2 max-h-40 overflow-y-auto">
                {selectedFiles.map((fileStatus, index) => (
                  <div key={index} className="flex items-center gap-3 p-3 bg-neutral-50 rounded-xl border border-neutral-100">
                    <div className="w-8 h-8 rounded-lg bg-primary-100 flex items-center justify-center flex-shrink-0">
                      <FileText className="h-4 w-4 text-primary-600" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-neutral-900 truncate">{fileStatus.file.name}</p>
                      <p className="text-xs text-neutral-500">
                        {formatFileSize(fileStatus.file.size)}
                      </p>
                    </div>
                    {!isProcessing && (
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => removeFile(index)}
                        className="h-8 w-8 text-neutral-400 hover:text-red-500 hover:bg-red-50"
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                ))}
              </div>

              {/* Start Extraction Button */}
              <div className="w-full pt-2">
                <Button
                  onClick={handleProcessFiles}
                  className="w-full"
                  variant={selectedFiles.length === 0 ? "outline" : "primary"}
                  disabled={isProcessing}
                >
                  {isProcessing ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Processing...
                    </>
                  ) : selectedFiles.length === 0 ? (
                    "Select Files to Start Extraction"
                  ) : (
                    `Start Extraction (${selectedFiles.length} file${selectedFiles.length > 1 ? 's' : ''})`
                  )}
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <div className="mt-6 text-center">
        <p className="text-xs text-neutral-400">
          Supported Formats: PDF, DOCX (Max 50MB each) • Up to {maxFiles} files
        </p>
      </div>
    </div>
  );
};
