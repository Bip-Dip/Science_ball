import React from 'react';
import UploadPage from './features/documents/UploadPage';

export default function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-slate-900 text-white py-4 px-6 shadow-md">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-2 font-bold text-xl tracking-tight">
            <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center">
              <span className="text-white">KM</span>
            </div>
            R&D Knowledge Map
          </div>
          <nav className="flex gap-6 text-sm font-medium text-slate-300">
            <a href="#" className="hover:text-white transition-colors">Dashboard</a>
            <a href="#" className="text-white border-b-2 border-blue-500 pb-1">Documents</a>
            <a href="#" className="hover:text-white transition-colors">Search</a>
            <a href="#" className="hover:text-white transition-colors">Graph</a>
          </nav>
        </div>
      </header>

      <main className="flex-1 bg-slate-50 py-12 px-6">
        <UploadPage />
      </main>
    </div>
  );
}
