import React, { useState } from 'react';
import { Search, Filter, BrainCircuit, Loader2, AlertCircle } from 'lucide-react';
import { searchDocuments, SearchFilters, SearchResultItem } from '../../api/search';
import { getGroundedAnswer, AnswerResponse } from '../../api/answers';
import SearchResults from './components/SearchResults';
import AnswerPanel from './components/AnswerPanel';

export default function SearchPage() {
  const [query, setQuery] = useState('');
  const [filters, setFilters] = useState<SearchFilters>({
    practice_region: 'foreign',
    year_from: undefined,
    year_to: undefined,
    min_confidence: 0.6,
  });

  const [results, setResults] = useState<SearchResultItem[]>([]);
  const [answer, setAnswer] = useState<AnswerResponse | null>(null);
  const [status, setStatus] = useState<'idle' | 'loading-search' | 'loading-answer' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState('');

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setStatus('loading-search');
    setErrorMessage('');
    try {
      const data = await searchDocuments(query, filters);
      setResults(data);
      setStatus('idle');
    } catch (err: any) {
      setStatus('error');
      setErrorMessage(err.message || 'Search failed');
    }
  };

  const handleSynthesize = async () => {
    if (!query.trim()) return;

    setStatus('loading-answer');
    setErrorMessage('');
    try {
      const data = await getGroundedAnswer(query, filters);
      setAnswer(data);
      setStatus('idle');
    } catch (err: any) {
      setStatus('error');
      setErrorMessage(err.message || 'Synthesis failed');
    }
  };

  return (
    <div className="max-w-7xl mx-auto h-full flex flex-col gap-8">
      {/* Search Header & Filters */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 space-y-6">
        <div className="flex items-center gap-3 text-2xl font-bold text-slate-900">
          <Search className="w-6 h-6 text-blue-600" />
          Knowledge Search
        </div>

        <form onSubmit={handleSearch} className="grid grid-cols-1 lg:grid-cols-4 gap-6 items-end">
          <div className="lg:col-span-2 flex flex-col gap-2">
            <label className="text-sm font-medium text-slate-700">Research Question</label>
            <div className="relative">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="w-full pl-3 pr-10 py-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500 outline-none"
                placeholder="e.g., optimal catholyte circulation rate for nickel electrowinning..."
              />
              <button
                type="submit"
                className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                <Search className="w-4 h-4" />
              </button>
            </div>
          </div>

          <div className="flex flex-col gap-2">
            <label className="text-sm font-medium text-slate-700">Region</label>
            <select
              value={filters.practice_region}
              onChange={(e) => setFilters({ ...filters, practice_region: e.target.value as any })}
              className="px-3 py-2 border border-slate-300 rounded-md bg-white outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="domestic">Domestic (РФ)</option>
              <option value="foreign">Foreign (Мировая)</option>
            </select>
          </div>

          <div className="flex flex-col gap-2">
            <label className="text-sm font-medium text-slate-700">Min Confidence</label>
            <input
              type="number"
              step="0.1"
              min="0"
              max="1"
              value={filters.min_confidence}
              onChange={(e) => setFilters({ ...filters, min_confidence: parseFloat(e.target.value) })}
              className="px-3 py-2 border border-slate-300 rounded-md outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-4 lg:col-span-1">
             {/* Year range simplified for MVP layout */}
             <div className="flex flex-col gap-2">
                <label className="text-sm font-medium text-slate-700">From</label>
                <input
                  type="number"
                  value={filters.year_from || ''}
                  onChange={(e) => setFilters({ ...filters, year_from: parseInt(e.target.value) || undefined })}
                  className="px-3 py-2 border border-slate-300 rounded-md outline-none focus:ring-2 focus:ring-blue-500"
                />
             </div>
             <div className="flex flex-col gap-2">
                <label className="text-sm font-medium text-slate-700">To</label>
                <input
                  type="number"
                  value={filters.year_to || ''}
                  onChange={(e) => setFilters({ ...filters, year_to: parseInt(e.target.value) || undefined })}
                  className="px-3 py-2 border border-slate-300 rounded-md outline-none focus:ring-2 focus:ring-blue-500"
                />
             </div>
          </div>

          <button
            onClick={handleSynthesize}
            disabled={!query.trim() || status.includes('loading')}
            className="lg:col-span-4 w-full py-3 px-4 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-400 text-white font-semibold rounded-lg transition-colors flex items-center justify-center gap-2"
          >
            {status === 'loading-answer' ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <BrainCircuit className="w-5 h-5" />
            )}
            Synthesize Grounded Answer
          </button>
        </form>

        {status === 'error' && (
          <div className="p-4 rounded-lg bg-red-100 text-red-800 border border-red-200 flex items-center gap-3">
            <AlertCircle className="w-5 h-5" />
            <span className="text-sm">{errorMessage}</span>
          </div>
        )}
      </div >

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 flex-1">
        {/* Left Column: Evidence Results */}
        <div className="lg:col-span-5 flex flex-col h-[calc(100vh-300px)]">
          <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-4 px-2">
            Retrieved Evidence
          </h3>
          <div className="flex-1 overflow-y-auto pr-2">
             <SearchResults results={results} isLoading={status === 'loading-search'} />
          </div>
        </div>

        {/* Right Column: Synthesized Answer */}
        <div className="lg:col-span-7 flex flex-col h-[calc(100vh-300px)]">
          <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-4 px-2">
            Knowledge Synthesis
          </h3>
          <div className="flex-1 overflow-y-auto pr-2">
             <AnswerPanel answer={answer} isLoading={status === 'loading-answer'} />
          </div>
        </div>
      </div>
    </div>
  );
}
