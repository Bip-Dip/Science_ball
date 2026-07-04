import React from 'react';
import { Search, Filter, Database, BrainCircuit, AlertTriangle, Info } from 'lucide-react';

export interface SearchResultItem {
  chunk_id: string;
  document_id: string;
  text: string;
  score: number;
  source_type: string;
  year: number;
  geography: string[];
}

interface SearchResultsProps {
  results: SearchResultItem[];
  isLoading: boolean;
}

export default function SearchResults({ results, isLoading }: SearchResultsProps) {
  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-slate-400">
        <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-4" />
        <p>Searching knowledge base...</p>
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-slate-400 border-2 border-dashed border-slate-200 rounded-xl">
        <Database className="w-8 h-8 mb-2 opacity-50" />
        <p>No evidence found for this query</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between text-sm font-medium text-slate-500 mb-2">
        <span>Found {results.length} evidence chunks</span>
        <span>Sorted by relevance</span>
      </div>
      {results.map((item) => (
        <div
          key={item.chunk_id}
          className="p-4 bg-white rounded-lg border border-slate-200 shadow-sm hover:border-blue-300 transition-colors group"
        >
          <div className="flex justify-between items-start mb-2">
            <span className="text-xs font-mono text-blue-600 bg-blue-50 px-2 py-1 rounded">
              Doc: {item.document_id}
            </span>
            <span className="text-xs text-slate-400">
              Score: {(item.score * 100).toFixed(1)}%
            </span>
          </div>
          <p className="text-sm text-slate-700 leading-relaxed mb-3 italic">
            "{item.text}"
          </p>
          <div className="flex gap-3 text-xs text-slate-500 border-t pt-2 mt-2">
            <span className="flex items-center gap-1 capitalize">
              <Info className="w-3 h-3" /> {item.source_type}
            </span>
            <span>•</span>
            <span>{item.year}</span>
            <span>•</span>
            <span className="truncate max-w-[150px]">
              {item.geography.join(', ') || 'Global'}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}
