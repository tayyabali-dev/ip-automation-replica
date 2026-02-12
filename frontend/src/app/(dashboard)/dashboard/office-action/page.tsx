'use client';

import React, { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Upload, FileText, Loader2, AlertCircle, ArrowRight } from 'lucide-react';
import { cn, formatFileSize } from '@/lib/utils';
import axios from '@/lib/axios';

export default function OfficeActionPage() {
    const router = useRouter();
    const [file, setFile] = useState<File | null>(null);
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [isDragging, setIsDragging] = useState(false);

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

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            const droppedFile = e.dataTransfer.files[0];
            if (droppedFile.type === 'application/pdf') {
                setFile(droppedFile);
                setError(null);
            } else {
                setError('Please upload a PDF file.');
            }
        }
    }, []);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            setFile(e.target.files[0]);
            setError(null);
        }
    };

    const handleUpload = async () => {
        if (!file) {
            setError('Please select a PDF file.');
            return;
        }

        setUploading(true);
        setError(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await axios.post('/office-actions/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            const { document_id, job_id } = response.data;
            router.push(`/dashboard/office-action/${document_id}/analysis?jobId=${job_id}`);
        } catch (err: any) {
            console.error('Upload failed:', err);
            setError(err.response?.data?.detail || 'Upload failed. Please try again.');
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Page Header */}
            <div className="flex items-center gap-4">
                <Link
                    href="/dashboard"
                    className="p-2 rounded-lg hover:bg-neutral-100 text-neutral-500 hover:text-neutral-900 transition-colors"
                >
                    <ArrowLeft className="w-5 h-5" />
                </Link>
                <div>
                    <h1 className="text-2xl font-semibold tracking-tight text-neutral-900">
                        Office Action Analyzer
                    </h1>
                    <p className="text-sm text-neutral-500">
                        Extract and analyze USPTO Office Actions
                    </p>
                </div>
            </div>

            <div className="max-w-xl mx-auto">
                <Card>
                    <CardHeader>
                        <CardTitle>Upload Office Action</CardTitle>
                        <CardDescription>
                            Upload a PDF of a USPTO Office Action to extract and analyze its contents.
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        {/* Drop Zone */}
                        <div
                            className={cn(
                                "border-2 border-dashed rounded-xl p-8 transition-all duration-300 cursor-pointer",
                                isDragging
                                    ? "border-primary-500 bg-primary-50/50"
                                    : file
                                    ? "border-emerald-300 bg-emerald-50/50"
                                    : "border-neutral-200 hover:border-neutral-300",
                                error ? "border-red-300 bg-red-50/50" : ""
                            )}
                            onDragOver={handleDragOver}
                            onDragLeave={handleDragLeave}
                            onDrop={handleDrop}
                            onClick={() => document.getElementById('file-input')?.click()}
                        >
                            <div className="flex flex-col items-center text-center">
                                <div className={cn(
                                    "w-14 h-14 rounded-full flex items-center justify-center mb-4",
                                    file ? "bg-emerald-100" : "bg-neutral-100"
                                )}>
                                    {file ? (
                                        <FileText className="w-7 h-7 text-emerald-600" />
                                    ) : (
                                        <Upload className={cn(
                                            "w-7 h-7",
                                            isDragging ? "text-primary-500" : "text-neutral-400"
                                        )} />
                                    )}
                                </div>

                                {file ? (
                                    <div>
                                        <p className="text-sm font-medium text-neutral-900">{file.name}</p>
                                        <p className="text-xs text-neutral-500 mt-1">
                                            {formatFileSize(file.size)}
                                        </p>
                                        <button
                                            className="text-xs text-primary-500 hover:text-primary-600 mt-2 font-medium"
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                setFile(null);
                                            }}
                                        >
                                            Change file
                                        </button>
                                    </div>
                                ) : (
                                    <div>
                                        <p className="text-sm font-medium text-neutral-700">
                                            Drop your PDF here
                                        </p>
                                        <p className="text-xs text-neutral-500 mt-1">
                                            or click to browse
                                        </p>
                                    </div>
                                )}
                            </div>

                            <input
                                type="file"
                                id="file-input"
                                accept=".pdf"
                                className="hidden"
                                onChange={handleFileChange}
                                disabled={uploading}
                            />
                        </div>

                        {error && (
                            <div className="flex items-center gap-2 text-red-600 text-sm p-3 bg-red-50 rounded-lg border border-red-100">
                                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                                <span>{error}</span>
                            </div>
                        )}

                        <Button
                            className="w-full group"
                            variant="primary"
                            onClick={handleUpload}
                            disabled={!file || uploading}
                        >
                            {uploading ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Analyzing Document...
                                </>
                            ) : (
                                <>
                                    Analyze Document
                                    <ArrowRight className="ml-2 h-4 w-4 opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-300" />
                                </>
                            )}
                        </Button>

                        <p className="text-xs text-center text-neutral-400">
                            Supported format: PDF • Max file size: 50MB
                        </p>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
