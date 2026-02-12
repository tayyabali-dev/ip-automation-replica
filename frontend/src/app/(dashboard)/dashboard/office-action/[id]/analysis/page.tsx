'use client';

import React, { useEffect, useState, Suspense } from 'react';
import { useParams, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import axios from '@/lib/axios';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { OfficeActionData, JobStatus, DeadlineCalculation } from '@/lib/types';
import {
    ArrowLeft,
    Download,
    FileText,
    AlertTriangle,
    CheckCircle,
    Clock,
    Loader2,
    XCircle,
    ChevronDown,
    ChevronUp,
    Calendar,
    BookOpen,
    FileOutput
} from 'lucide-react';
import { cn } from '@/lib/utils';

// Loading fallback for Suspense
function AnalysisLoading() {
    return (
        <div className="flex flex-col items-center justify-center min-h-[60vh] animate-fade-in">
            <div className="w-20 h-20 rounded-full bg-primary-100 flex items-center justify-center mb-6">
                <Loader2 className="w-10 h-10 text-primary-500 animate-spin" />
            </div>
            <h2 className="text-2xl font-semibold text-neutral-900 mb-2">Loading...</h2>
        </div>
    );
}

function AnalysisContent() {
    const params = useParams();
    const searchParams = useSearchParams();
    const documentId = params.id as string;
    const jobId = searchParams.get('jobId');

    const [jobStatus, setJobStatus] = useState<JobStatus | null>(null);
    const [data, setData] = useState<OfficeActionData | null>(null);
    const [loading, setLoading] = useState(true);
    const [calculatingDeadlines, setCalculatingDeadlines] = useState(false);
    const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
        header: true,
        deadlines: true,
        rejections: true,
        claims: true,
        references: false
    });

    const toggleSection = (section: string) => {
        setExpandedSections(prev => ({ ...prev, [section]: !prev[section] }));
    };

    // Effect for polling job status (when coming from upload with jobId)
    useEffect(() => {
        if (!jobId || data) return;

        const interval = setInterval(async () => {
            try {
                const res = await axios.get(`/jobs/${jobId}`);
                setJobStatus(res.data);

                if (res.data.status === 'completed') {
                    clearInterval(interval);
                    fetchData();
                } else if (res.data.status === 'failed') {
                    clearInterval(interval);
                    setLoading(false);
                }
            } catch (err) {
                console.error("Error polling job:", err);
            }
        }, 2000);

        return () => clearInterval(interval);
    }, [jobId, data]);

    // Effect for loading existing data (when coming from history without jobId)
    useEffect(() => {
        if (jobId) return; // Skip if we have a jobId (handled by polling effect)
        fetchData();
    }, [documentId]);

    const fetchData = async () => {
        try {
            const res = await axios.get(`/office-actions/${documentId}`);
            setData(res.data);
        } catch (err) {
            console.error("Error fetching data:", err);
        } finally {
            setLoading(false);
        }
    };

    const handleDownloadReport = async () => {
        try {
            const response = await axios.get(`/office-actions/${documentId}/report`, {
                responseType: 'blob',
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `Office_Action_Report_${documentId}.docx`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (err) {
            console.error("Download failed:", err);
            alert("Failed to download report.");
        }
    };

    const handleDownloadResponseShell = async () => {
        try {
            const response = await axios.get(`/office-actions/${documentId}/response-shell`, {
                responseType: 'blob',
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `Response_Shell_${documentId}.docx`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (err) {
            console.error("Response shell download failed:", err);
            alert("Failed to download response shell.");
        }
    };

    const handleCalculateDeadlines = async () => {
        setCalculatingDeadlines(true);
        try {
            const response = await axios.post(`/office-actions/${documentId}/calculate-deadlines`);
            setData(prev => prev ? { ...prev, deadline_calculation: response.data } : null);
        } catch (err) {
            console.error("Deadline calculation failed:", err);
            alert("Failed to calculate deadlines. Make sure the mailing date is set.");
        } finally {
            setCalculatingDeadlines(false);
        }
    };

    // Loading State
    if (loading || (jobStatus && jobStatus.status !== 'completed' && jobStatus.status !== 'failed')) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[60vh] animate-fade-in">
                <div className="w-20 h-20 rounded-full bg-primary-100 flex items-center justify-center mb-6">
                    <Loader2 className="w-10 h-10 text-primary-500 animate-spin" />
                </div>
                <h2 className="text-2xl font-semibold text-neutral-900 mb-2">Analyzing Document</h2>
                <p className="text-neutral-500 mb-6">This may take a moment...</p>

                <div className="w-full max-w-md">
                    <div className="h-2 w-full bg-neutral-100 rounded-full overflow-hidden mb-2">
                        <div
                            className="h-full bg-primary-500 transition-all duration-500 ease-out"
                            style={{ width: `${jobStatus?.progress_percentage || 0}%` }}
                        />
                    </div>
                    <p className="text-sm text-neutral-500 text-center">
                        {jobStatus?.status === 'processing' ? 'Processing' : 'Initializing'}...{' '}
                        {jobStatus?.progress_percentage || 0}%
                    </p>
                </div>
            </div>
        );
    }

    // Failed State
    if (jobStatus?.status === 'failed') {
        return (
            <div className="flex flex-col items-center justify-center min-h-[60vh] animate-fade-in">
                <div className="w-20 h-20 rounded-full bg-red-100 flex items-center justify-center mb-6">
                    <XCircle className="w-10 h-10 text-red-500" />
                </div>
                <h2 className="text-2xl font-semibold text-neutral-900 mb-2">Analysis Failed</h2>
                <p className="text-neutral-500 mb-6 max-w-md text-center">
                    {jobStatus.error_details || 'An error occurred while processing the document.'}
                </p>
                <Button asChild>
                    <Link href="/dashboard/office-action">
                        <ArrowLeft className="mr-2 h-4 w-4" />
                        Try Again
                    </Link>
                </Button>
            </div>
        );
    }

    if (!data) return null;

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Page Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="flex items-center gap-4">
                    <Link
                        href="/dashboard/office-action"
                        className="p-2 rounded-lg hover:bg-neutral-100 text-neutral-500 hover:text-neutral-900 transition-colors"
                    >
                        <ArrowLeft className="w-5 h-5" />
                    </Link>
                    <div>
                        <h1 className="text-2xl font-semibold tracking-tight text-neutral-900">
                            Analysis Results
                        </h1>
                        <p className="text-sm text-neutral-500">
                            {data.header.application_number || 'Office Action Analysis'}
                        </p>
                    </div>
                </div>
                <div className="flex flex-wrap gap-3">
                    <Button variant="outline" onClick={handleDownloadResponseShell}>
                        <FileOutput className="mr-2 h-4 w-4" />
                        Response Shell
                    </Button>
                    <Button variant="primary" onClick={handleDownloadReport}>
                        <Download className="mr-2 h-4 w-4" />
                        Download Report
                    </Button>
                </div>
            </div>

            {/* Content */}
            <div className="grid gap-6">
                {/* Header Info */}
                <Card>
                    <CardHeader
                        className="cursor-pointer"
                        onClick={() => toggleSection('header')}
                    >
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <FileText className="w-5 h-5 text-neutral-400" />
                                <CardTitle>Application Details</CardTitle>
                            </div>
                            {expandedSections.header ? (
                                <ChevronUp className="w-5 h-5 text-neutral-400" />
                            ) : (
                                <ChevronDown className="w-5 h-5 text-neutral-400" />
                            )}
                        </div>
                    </CardHeader>
                    {expandedSections.header && (
                        <CardContent className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            <div className="space-y-1.5">
                                <label className="text-xs font-medium text-neutral-500 uppercase tracking-wider">
                                    Application Number
                                </label>
                                <Input
                                    value={data.header.application_number || ''}
                                    onChange={(e) => setData({...data, header: {...data.header, application_number: e.target.value}})}
                                />
                            </div>
                            <div className="space-y-1.5">
                                <label className="text-xs font-medium text-neutral-500 uppercase tracking-wider">
                                    Filing Date
                                </label>
                                <Input
                                    value={data.header.filing_date || ''}
                                    onChange={(e) => setData({...data, header: {...data.header, filing_date: e.target.value}})}
                                />
                            </div>
                            <div className="space-y-1.5">
                                <label className="text-xs font-medium text-neutral-500 uppercase tracking-wider">
                                    First Named Inventor
                                </label>
                                <Input
                                    value={data.header.first_named_inventor || ''}
                                    onChange={(e) => setData({...data, header: {...data.header, first_named_inventor: e.target.value}})}
                                />
                            </div>
                            <div className="space-y-1.5">
                                <label className="text-xs font-medium text-neutral-500 uppercase tracking-wider">
                                    Attorney Docket Number
                                </label>
                                <Input
                                    value={data.header.attorney_docket_number || ''}
                                    onChange={(e) => setData({...data, header: {...data.header, attorney_docket_number: e.target.value}})}
                                />
                            </div>
                            <div className="space-y-1.5">
                                <label className="text-xs font-medium text-neutral-500 uppercase tracking-wider">
                                    Title of Invention
                                </label>
                                <Input
                                    value={data.header.title_of_invention || ''}
                                    onChange={(e) => setData({...data, header: {...data.header, title_of_invention: e.target.value}})}
                                />
                            </div>
                            <div className="space-y-1.5">
                                <label className="text-xs font-medium text-neutral-500 uppercase tracking-wider">
                                    Office Action Type
                                </label>
                                <Input
                                    value={data.header.office_action_type || ''}
                                    onChange={(e) => setData({...data, header: {...data.header, office_action_type: e.target.value}})}
                                    placeholder="e.g., Non-Final, Final"
                                />
                            </div>
                            <div className="space-y-1.5">
                                <label className="text-xs font-medium text-neutral-500 uppercase tracking-wider">
                                    Mailing Date
                                </label>
                                <Input
                                    value={data.header.office_action_date || ''}
                                    onChange={(e) => setData({...data, header: {...data.header, office_action_date: e.target.value}})}
                                />
                            </div>
                            <div className="space-y-1.5">
                                <label className="text-xs font-medium text-neutral-500 uppercase tracking-wider">
                                    Response Deadline
                                </label>
                                <Input
                                    value={data.header.response_deadline || ''}
                                    onChange={(e) => setData({...data, header: {...data.header, response_deadline: e.target.value}})}
                                />
                            </div>
                            <div className="space-y-1.5">
                                <label className="text-xs font-medium text-neutral-500 uppercase tracking-wider">
                                    Examiner Name
                                </label>
                                <Input
                                    value={data.header.examiner_name || ''}
                                    onChange={(e) => setData({...data, header: {...data.header, examiner_name: e.target.value}})}
                                />
                            </div>
                            <div className="space-y-1.5">
                                <label className="text-xs font-medium text-neutral-500 uppercase tracking-wider">
                                    Art Unit
                                </label>
                                <Input
                                    value={data.header.art_unit || ''}
                                    onChange={(e) => setData({...data, header: {...data.header, art_unit: e.target.value}})}
                                />
                            </div>
                            <div className="space-y-1.5">
                                <label className="text-xs font-medium text-neutral-500 uppercase tracking-wider">
                                    Examiner Phone
                                </label>
                                <Input
                                    value={data.header.examiner_phone || ''}
                                    onChange={(e) => setData({...data, header: {...data.header, examiner_phone: e.target.value}})}
                                />
                            </div>
                            <div className="space-y-1.5">
                                <label className="text-xs font-medium text-neutral-500 uppercase tracking-wider">
                                    Examiner Email
                                </label>
                                <Input
                                    value={data.header.examiner_email || ''}
                                    onChange={(e) => setData({...data, header: {...data.header, examiner_email: e.target.value}})}
                                />
                            </div>
                        </CardContent>
                    )}
                </Card>

                {/* Deadline Calculation */}
                <Card>
                    <CardHeader
                        className="cursor-pointer"
                        onClick={() => toggleSection('deadlines')}
                    >
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <Calendar className="w-5 h-5 text-blue-500" />
                                <CardTitle>Response Deadlines</CardTitle>
                            </div>
                            {expandedSections.deadlines ? (
                                <ChevronUp className="w-5 h-5 text-neutral-400" />
                            ) : (
                                <ChevronDown className="w-5 h-5 text-neutral-400" />
                            )}
                        </div>
                    </CardHeader>
                    {expandedSections.deadlines && (
                        <CardContent>
                            {data.deadline_calculation ? (
                                <div className="space-y-4">
                                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                        <div className="p-3 bg-neutral-50 rounded-lg">
                                            <p className="text-xs text-neutral-500 uppercase mb-1">Mailing Date</p>
                                            <p className="font-medium">{data.deadline_calculation.mailing_date}</p>
                                        </div>
                                        <div className="p-3 bg-green-50 rounded-lg">
                                            <p className="text-xs text-green-600 uppercase mb-1">Statutory Deadline</p>
                                            <p className="font-medium text-green-700">{data.deadline_calculation.statutory_deadline}</p>
                                        </div>
                                        <div className="p-3 bg-red-50 rounded-lg">
                                            <p className="text-xs text-red-600 uppercase mb-1">Maximum Deadline</p>
                                            <p className="font-medium text-red-700">{data.deadline_calculation.maximum_deadline}</p>
                                        </div>
                                        <div className="p-3 bg-neutral-50 rounded-lg">
                                            <p className="text-xs text-neutral-500 uppercase mb-1">SSP</p>
                                            <p className="font-medium">{data.deadline_calculation.shortened_statutory_period} months</p>
                                        </div>
                                    </div>

                                    {/* Deadline Tiers Table */}
                                    <div className="overflow-x-auto">
                                        <table className="w-full text-sm">
                                            <thead>
                                                <tr className="border-b border-neutral-200">
                                                    <th className="text-left py-2 px-3 font-medium text-neutral-500">Deadline</th>
                                                    <th className="text-left py-2 px-3 font-medium text-neutral-500">Extension</th>
                                                    <th className="text-right py-2 px-3 font-medium text-neutral-500">Micro ($)</th>
                                                    <th className="text-right py-2 px-3 font-medium text-neutral-500">Small ($)</th>
                                                    <th className="text-right py-2 px-3 font-medium text-neutral-500">Large ($)</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {data.deadline_calculation.tiers.map((tier, idx) => (
                                                    <tr
                                                        key={idx}
                                                        className={cn(
                                                            "border-b border-neutral-100",
                                                            tier.is_past && "bg-red-50 text-red-700"
                                                        )}
                                                    >
                                                        <td className="py-2 px-3">
                                                            {tier.deadline_date}
                                                            {tier.is_past && <span className="ml-2 text-xs">(PAST)</span>}
                                                        </td>
                                                        <td className="py-2 px-3">
                                                            {tier.months_extension === 0 ? 'None' : `${tier.months_extension} month(s)`}
                                                        </td>
                                                        <td className="py-2 px-3 text-right">${tier.extension_fee_micro.toLocaleString()}</td>
                                                        <td className="py-2 px-3 text-right">${tier.extension_fee_small.toLocaleString()}</td>
                                                        <td className="py-2 px-3 text-right">${tier.extension_fee_large.toLocaleString()}</td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>

                                    {data.deadline_calculation.notes.length > 0 && (
                                        <div className="text-xs text-neutral-500 space-y-1">
                                            {data.deadline_calculation.notes.map((note, idx) => (
                                                <p key={idx}>* {note}</p>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            ) : (
                                <div className="text-center py-6">
                                    <Calendar className="w-10 h-10 mx-auto mb-2 text-neutral-300" />
                                    <p className="text-neutral-500 mb-4">Deadline calculation not available</p>
                                    <Button
                                        variant="outline"
                                        onClick={handleCalculateDeadlines}
                                        disabled={calculatingDeadlines}
                                    >
                                        {calculatingDeadlines ? (
                                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                        ) : (
                                            <Calendar className="mr-2 h-4 w-4" />
                                        )}
                                        Calculate Deadlines
                                    </Button>
                                </div>
                            )}
                        </CardContent>
                    )}
                </Card>

                {/* Rejections */}
                <Card>
                    <CardHeader
                        className="cursor-pointer"
                        onClick={() => toggleSection('rejections')}
                    >
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <AlertTriangle className="w-5 h-5 text-amber-500" />
                                <CardTitle>Rejections</CardTitle>
                                <Badge variant="warning">{data.rejections.length}</Badge>
                            </div>
                            {expandedSections.rejections ? (
                                <ChevronUp className="w-5 h-5 text-neutral-400" />
                            ) : (
                                <ChevronDown className="w-5 h-5 text-neutral-400" />
                            )}
                        </div>
                    </CardHeader>
                    {expandedSections.rejections && (
                        <CardContent className="space-y-4">
                            {data.rejections.length === 0 ? (
                                <div className="text-center py-8 text-neutral-500">
                                    <CheckCircle className="w-10 h-10 mx-auto mb-2 text-emerald-400" />
                                    <p>No rejections detected in this Office Action.</p>
                                </div>
                            ) : (
                                data.rejections.map((rej, idx) => (
                                    <div
                                        key={idx}
                                        className="border border-neutral-200 rounded-xl p-4 space-y-4"
                                    >
                                        <div className="flex flex-wrap items-center gap-2">
                                            <Badge variant="danger">
                                                {rej.rejection_type_normalized || rej.rejection_type}
                                            </Badge>
                                            <span className="text-sm font-medium text-neutral-700">
                                                Rejection #{idx + 1}
                                            </span>
                                            {rej.is_aia !== undefined && (
                                                <Badge variant="default">
                                                    {rej.is_aia ? 'AIA' : 'Pre-AIA'}
                                                </Badge>
                                            )}
                                            {rej.statutory_basis && (
                                                <span className="text-sm text-neutral-500">
                                                    ({rej.statutory_basis})
                                                </span>
                                            )}
                                        </div>

                                        <div className="text-sm text-neutral-600">
                                            <span className="font-medium">Claims: </span>
                                            {rej.affected_claims.join(', ')}
                                        </div>

                                        {/* Prior Art Combinations for 103 */}
                                        {rej.prior_art_combinations && rej.prior_art_combinations.length > 0 && (
                                            <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 space-y-2">
                                                <p className="text-xs font-medium text-amber-800 uppercase">Prior Art Combinations</p>
                                                {rej.prior_art_combinations.map((combo, cIdx) => (
                                                    <div key={cIdx} className="text-sm">
                                                        <p><span className="font-medium">Primary:</span> {combo.primary_reference_id}</p>
                                                        {combo.secondary_reference_ids.length > 0 && (
                                                            <p><span className="font-medium">Secondary:</span> {combo.secondary_reference_ids.join(', ')}</p>
                                                        )}
                                                        {combo.motivation_to_combine && (
                                                            <p className="text-xs text-amber-700 mt-1">
                                                                <span className="font-medium">Motivation:</span> {combo.motivation_to_combine}
                                                            </p>
                                                        )}
                                                    </div>
                                                ))}
                                            </div>
                                        )}

                                        <div className="space-y-2">
                                            <label className="text-xs font-medium text-neutral-500 uppercase tracking-wider">
                                                Examiner Reasoning
                                            </label>
                                            <Textarea
                                                value={rej.examiner_reasoning}
                                                onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => {
                                                    const newRejections = [...data.rejections];
                                                    newRejections[idx].examiner_reasoning = e.target.value;
                                                    setData({...data, rejections: newRejections});
                                                }}
                                                rows={4}
                                                className="resize-none"
                                            />
                                        </div>
                                    </div>
                                ))
                            )}
                        </CardContent>
                    )}
                </Card>

                {/* All References */}
                {data.all_references && data.all_references.length > 0 && (
                    <Card>
                        <CardHeader
                            className="cursor-pointer"
                            onClick={() => toggleSection('references')}
                        >
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                    <BookOpen className="w-5 h-5 text-purple-500" />
                                    <CardTitle>Prior Art References</CardTitle>
                                    <Badge variant="default">{data.all_references.length}</Badge>
                                </div>
                                {expandedSections.references ? (
                                    <ChevronUp className="w-5 h-5 text-neutral-400" />
                                ) : (
                                    <ChevronDown className="w-5 h-5 text-neutral-400" />
                                )}
                            </div>
                        </CardHeader>
                        {expandedSections.references && (
                            <CardContent>
                                <div className="overflow-x-auto">
                                    <table className="w-full text-sm">
                                        <thead>
                                            <tr className="border-b border-neutral-200">
                                                <th className="text-left py-2 px-3 font-medium text-neutral-500">ID</th>
                                                <th className="text-left py-2 px-3 font-medium text-neutral-500">Reference</th>
                                                <th className="text-left py-2 px-3 font-medium text-neutral-500">Type</th>
                                                <th className="text-left py-2 px-3 font-medium text-neutral-500">Cited Sections</th>
                                                <th className="text-left py-2 px-3 font-medium text-neutral-500">Used In</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {data.all_references.map((ref, idx) => (
                                                <tr key={idx} className="border-b border-neutral-100">
                                                    <td className="py-2 px-3 font-mono text-xs">{ref.reference_id}</td>
                                                    <td className="py-2 px-3">
                                                        {ref.short_name && <span className="font-medium">{ref.short_name} - </span>}
                                                        {ref.identifier}
                                                    </td>
                                                    <td className="py-2 px-3">{ref.reference_type}</td>
                                                    <td className="py-2 px-3 text-xs">{ref.relevant_sections || '-'}</td>
                                                    <td className="py-2 px-3 text-xs">
                                                        {ref.used_in_rejection_indices?.map(i => `#${i + 1}`).join(', ') || '-'}
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </CardContent>
                        )}
                    </Card>
                )}

                {/* Claims Status */}
                <Card>
                    <CardHeader
                        className="cursor-pointer"
                        onClick={() => toggleSection('claims')}
                    >
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <Clock className="w-5 h-5 text-blue-500" />
                                <CardTitle>Claims Status</CardTitle>
                                <Badge variant="info">{data.claims_status.length}</Badge>
                            </div>
                            {expandedSections.claims ? (
                                <ChevronUp className="w-5 h-5 text-neutral-400" />
                            ) : (
                                <ChevronDown className="w-5 h-5 text-neutral-400" />
                            )}
                        </div>
                    </CardHeader>
                    {expandedSections.claims && (
                        <CardContent>
                            {data.claims_status.length === 0 ? (
                                <div className="text-center py-8 text-neutral-500">
                                    <p>No claims data available.</p>
                                </div>
                            ) : (
                                <div className="overflow-x-auto">
                                    <table className="w-full">
                                        <thead>
                                            <tr className="border-b border-neutral-200">
                                                <th className="text-left py-3 px-4 text-xs font-medium text-neutral-500 uppercase tracking-wider">
                                                    Claim No.
                                                </th>
                                                <th className="text-left py-3 px-4 text-xs font-medium text-neutral-500 uppercase tracking-wider">
                                                    Status
                                                </th>
                                                <th className="text-left py-3 px-4 text-xs font-medium text-neutral-500 uppercase tracking-wider">
                                                    Type
                                                </th>
                                                <th className="text-left py-3 px-4 text-xs font-medium text-neutral-500 uppercase tracking-wider">
                                                    Parent
                                                </th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {data.claims_status.map((claim, idx) => (
                                                <tr key={idx} className="border-b border-neutral-100 last:border-0">
                                                    <td className="py-3 px-4">
                                                        <Input
                                                            value={claim.claim_number || ''}
                                                            onChange={(e) => {
                                                                const newClaims = [...data.claims_status];
                                                                newClaims[idx].claim_number = e.target.value;
                                                                setData({...data, claims_status: newClaims});
                                                            }}
                                                            className="h-9"
                                                        />
                                                    </td>
                                                    <td className="py-3 px-4">
                                                        <Input
                                                            value={claim.status || ''}
                                                            onChange={(e) => {
                                                                const newClaims = [...data.claims_status];
                                                                newClaims[idx].status = e.target.value;
                                                                setData({...data, claims_status: newClaims});
                                                            }}
                                                            className="h-9"
                                                        />
                                                    </td>
                                                    <td className="py-3 px-4">
                                                        <Input
                                                            value={claim.dependency_type || ''}
                                                            onChange={(e) => {
                                                                const newClaims = [...data.claims_status];
                                                                newClaims[idx].dependency_type = e.target.value;
                                                                setData({...data, claims_status: newClaims});
                                                            }}
                                                            className="h-9"
                                                        />
                                                    </td>
                                                    <td className="py-3 px-4">
                                                        <Input
                                                            value={claim.parent_claim || ''}
                                                            onChange={(e) => {
                                                                const newClaims = [...data.claims_status];
                                                                newClaims[idx].parent_claim = e.target.value;
                                                                setData({...data, claims_status: newClaims});
                                                            }}
                                                            className="h-9"
                                                            placeholder="-"
                                                        />
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}
                        </CardContent>
                    )}
                </Card>
            </div>
        </div>
    );
}

// Main page component with Suspense boundary for useSearchParams
export default function AnalysisPage() {
    return (
        <Suspense fallback={<AnalysisLoading />}>
            <AnalysisContent />
        </Suspense>
    );
}
