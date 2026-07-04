import React, { useState } from 'react';
import { Upload, FileText, AlertCircle, CheckCircle2, Loader2 } from 'lucide-react';
import { uploadDocument } from '../../api/client';

const SOURCE_TYPES = ['publication', 'patent', 'report', 'handbook', 'experiment'];
const ACCESS_LEVELS = ['public', 'internal', 'confidential', 'restricted'];

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState('');
  const [sourceType, setSourceType] = useState(SOURCE_TYPES[0]);
  const [accessLevel, setAccessLevel] = useState(ACCESS_LEVELS[1]);
  const [language, setLanguage] = useState('ru');
  const [year, setYear] = useState('');

  const [status, setStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');
  const [documentId, setDocumentId] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setStatus('uploading');
    setMessage('');
    setDocumentId(null);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('title', title);
      formData.append('source_type', sourceType);
      formData.append('access_level', accessLevel);
      formData.append('language', language);
      if (year) formData.append('year', year);

      const result = await uploadDocument(formData);
      setDocumentId(result.document_id);
      setStatus('success');
      setMessage('Document uploaded successfully!');
    } catch (err: any) {
      setStatus('error');
      setMessage(err.message || 'An unexpected error occurred');
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Upload className="w-6 h-6" />
          Upload Document
        </h1>
        <p className="text-slate-500">Add new scientific sources to the Knowledge Map</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6 bg-white p-8 rounded-xl shadow-sm border border-slate-200">
        <div className="grid grid-cols-1 gap-6">
          {/* File Input */}
          <div className="flex flex-col gap-2">
            <label className="text-sm font-medium text-slate-700">Document File</label>
            <div
              className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                file ? 'border-green-500 bg-green-50' : 'border-slate-300 hover:border-blue-500 bg-slate-50'
              }`}
            >
              <input
                type="file"
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                accept=".pdf,.docx,.txt"
              />
              <div className="flex flex-col items-center gap-2">
                <FileText className={`w-8 h-8 ${file ? 'text-green-500' : 'text-slate-400'}`} />
                <span className="text-sm text-slate-600">
                  {file ? file.name : 'Click to upload or drag and drop'}
                </span>
                <span className="text-xs text-slate-400">PDF, DOCX, TXT up to 50MB</span>
              </div>
            </div>
          </div>

          {/* Basic Info */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex flex-col gap-2">
              <label className="text-sm font-medium text-slate-700">Title</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="px-3 py-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500 outline-none transition-all"
                placeholder="Enter document title"
                required
              />
            </div>
            <div className="flex flex-col gap-2">
              <label className="text-sm font-medium text-slate-700">Source Type</label>
              <select
                value={sourceType}
                onChange={(e) => setSourceType(e.target.value)}
                className="px-3 py-2 border border-slate-300 rounded-md bg-white focus:ring-2 focus:ring-blue-500 outline-none"
              >
                {SOURCE_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex flex-col gap-2">
              <label className="text-sm font-medium text-slate-700">Access Level</label>
              <select
                value={accessLevel}
                onChange={(e) => setAccessLevel(e.target.value)}
                className="px-3 py-2 border border-slate-300 rounded-md bg-white focus:ring-2 focus:ring-blue-500 outline-none"
              >
                {ACCESS_LEVELS.map(l => <option key={l} value={l}>{l}</option>)}
              </select>
            </div>
            <div className="flex flex-col gap-2">
              <label className="text-sm font-medium text-slate-700">Language</label>
              <input
                type="text"
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="px-3 py-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500 outline-none"
              />
            </div>
            <div className="flex flex-col gap-2">
              <label className="text-sm font-medium text-slate-700">Year</label>
              <input
                type="number"
                value={year}
                onChange={(e) => setYear(e.target.value)}
                className="px-3 py-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500 outline-none"
                placeholder="YYYY"
              />
            </div>
          </div>
        </div>

        {/* Status Messages */}
        {status !== 'idle' && (
          <div className={`p-4 rounded-lg flex items-center gap-3 ${
            status === 'success' ? 'bg-green-100 text-green-800 border border-green-200' :
            status === 'error' ? 'bg-red-100 text-red-800 border border-red-200' :
            'bg-blue-100 text-blue-800 border border-blue-200'
          }`}>
            {status === 'uploading' && <Loader2 className="w-5 h-5 animate-spin" />}
            {status === 'success' && <CheckCircle2 className="w-5 h-5" />}
            {status === 'error' && <AlertCircle className="w-5 h-5" />}
            <div className="text-sm">
              {message}
              {documentId && <span className="ml-2 font-mono font-bold">ID: {documentId}</span>}
            </div>
          </div>
        )}

        <button
          type="submit"
          disabled={status === 'uploading' || !file}
          className="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-400 text-white font-semibold rounded-lg transition-colors flex items-center justify-center gap-2"
        >
          {status === 'uploading' ? (
            <> <Loader2 className="w-5 h-5 animate-spin" /> Uploading... </>
          ) : (
            <> <Upload className="w-5 h-5" /> Start Ingestion </>
          )}
        </button>
      </form>
    </div>
  );
}
