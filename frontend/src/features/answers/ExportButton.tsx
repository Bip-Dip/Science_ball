import React, { useState } from 'react';
import { Download } from 'lucide-react';
import { exportToMarkdown } from '../../api/exports';
import { AnswerResponse } from '../../api/answers';

interface ExportButtonProps {
  answer: AnswerResponse;
}

export default function ExportButton({ answer }: ExportButtonProps) {
  const [isExporting, setIsExporting] = useState(false);

  const handleExport = async () => {
    setIsExporting(true);
    try {
      const blob = await exportToMarkdown(answer);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'knowledge_map_export.md';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      a.remove();
    } catch (error) {
      console.error('Export failed:', error);
      alert('Failed to export answer as Markdown');
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <button
      onClick={handleExport}
      disabled={isExporting}
      className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium text-slate-600 bg-white border border-slate-200 rounded-md hover:bg-slate-50 transition-colors disabled:opacity-50"
    >
      <Download className="w-3 h-3" />
      {isExporting ? 'Exporting...' : 'Export MD'}
    </button>
  );
}
