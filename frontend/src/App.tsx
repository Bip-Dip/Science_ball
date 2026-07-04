import React from 'react';
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import UploadPage from './features/documents/UploadPage';
import SearchPage from './features/search/SearchPage';
import GraphPage from './features/graph/GraphPage';

export default function App() {
  return (
    <BrowserRouter>
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
              <NavLink
                to="/documents"
                className={({ isActive }) =>
                  `hover:text-white transition-colors ${isActive ? 'text-white border-b-2 border-blue-500 pb-1' : ''}`
                }
              >
                Documents
              </NavLink>
              <NavLink
                to="/search"
                className={({ isActive }) =>
                  `hover:text-white transition-colors ${isActive ? 'text-white border-b-2 border-blue-500 pb-1' : ''}`
                }
              >
                Search
              </NavLink>
              <NavLink
                to="/graph"
                className={({ isActive }) =>
                  `hover:text-white transition-colors ${isActive ? 'text-white border-b-2 border-blue-500 pb-1' : ''}`
                }
              >
                Graph
              </NavLink>
            </nav>
          </div>
        </header>

        <main className="flex-1 bg-slate-50 py-12 px-6">
          <Routes>
            <Route path="/documents" element={<UploadPage />} />
            <Route path="/search" element={<SearchPage />} />
            <Route path="/graph" element={<GraphPage />} />
            {/* Default route redirects to search */}
            <Route path="/" element={<SearchPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
