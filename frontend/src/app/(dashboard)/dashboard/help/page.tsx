'use client';

import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { HelpCircle, FileText, Upload, Download, Mail } from 'lucide-react';

export default function HelpPage() {
  const faqs = [
    {
      icon: Upload,
      question: 'How do I upload a cover sheet?',
      answer: 'Go to "New Application" and drag & drop your PDF cover sheet or click to browse files. The system accepts PDF files up to 10MB.'
    },
    {
      icon: FileText,
      question: 'What is an Application Data Sheet (ADS)?',
      answer: 'An ADS is a USPTO form that contains bibliographic information about a patent application, including inventor details, correspondence address, and application information.'
    },
    {
      icon: Download,
      question: 'How do I download my generated ADS?',
      answer: 'After processing, you can download the generated ADS as a PDF from the results page. The file will be USPTO-compliant and ready for submission.'
    },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl md:text-3xl font-semibold tracking-tight text-neutral-900">
          Help Center
        </h1>
        <p className="text-neutral-500 mt-1">
          Find answers to common questions
        </p>
      </div>

      {/* FAQ Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <HelpCircle className="w-5 h-5 text-neutral-400" />
            Frequently Asked Questions
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {faqs.map((faq, index) => {
            const Icon = faq.icon;
            return (
              <div
                key={index}
                className="p-4 rounded-xl bg-neutral-50 border border-neutral-100"
              >
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-lg bg-white border border-neutral-200 flex items-center justify-center flex-shrink-0">
                    <Icon className="w-4 h-4 text-primary-500" />
                  </div>
                  <div>
                    <h3 className="font-medium text-neutral-900 mb-1">
                      {faq.question}
                    </h3>
                    <p className="text-sm text-neutral-500 leading-relaxed">
                      {faq.answer}
                    </p>
                  </div>
                </div>
              </div>
            );
          })}
        </CardContent>
      </Card>

      {/* Contact Support */}
      <Card>
        <CardHeader>
          <CardTitle>Need More Help?</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-3 p-4 rounded-xl bg-primary-50 border border-primary-100">
            <div className="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center">
              <Mail className="w-5 h-5 text-primary-600" />
            </div>
            <div>
              <p className="font-medium text-neutral-900">Contact Support</p>
              <p className="text-sm text-neutral-500">
                Email us at support@jwhd-ip.com
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
