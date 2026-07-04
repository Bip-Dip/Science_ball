import React from 'react';
import { BrainCircuit, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { AnswerResponse } from '../../../api/answers';

interface AnswerPanelProps {
  answer: AnswerResponse | null;
  isLoading: boolean;
}

export default function AnswerPanel({ answer, isLoading }: AnswerPanelProps) {
  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-slate-400 h-full">
        <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-4" />
        <p>Synthesizing grounded answer...</p>
      </div>
    );
  }

  if (!answer) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-slate-400 h-full border-2 border-dashed border-slate-200 rounded-xl bg-slate-50/50">
        <BrainCircuit className="w-8 h-8 mb-2 opacity-50" />
        <p className="text-center px-4">Enter a query and click "Synthesize Answer" to get an LLM-generated summary backed by evidence</p>
      </div>
    );
  }

  return (
    <div className="space-y-8 h-full overflow-y-auto pr-2">
      {/* Summary Section */}
      <section>
        <div className="flex items-center gap-2 mb-3 text-slate-900 font-bold text-lg">
          <BrainCircuit className="w-5 h-5 text-blue-600" />
          Grounded Answer
        </div>
        <div className="p-5 bg-white rounded-xl border border-blue-100 shadow-sm relative overflow-hidden">
          <div
            className={`absolute top-0 right-0 px-3 py-1 text-xs font-bold text-white ${
              answer.answer.confidence > 0.7 ? 'bg-green-500' :
              answer.answer.confidence > 0.4 ? 'bg-amber-500' : 'bg-red-500'
            }`}
          >
            Confidence: {(answer.answer.confidence * 100).toFixed(0)}%
          </div>
          <p className="text-slate-800 leading-relaxed text-lg">
            {answer.answer.summary}
          </p>
        </div>
      </section>

      {/* Evidence Table */}
      <section>
        <div className="flex items-center gap-2 mb-3 text-slate-900 font-bold text-md">
          <CheckCircle2 className="w-5 h-5 text-green-600" />
          Supporting Evidence
        </div>
        <div className="overflow-hidden border border-slate-200 rounded-lg shadow-sm">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-600 font-medium border-b border-slate-200">
              <tr>
                <th className="px-4 py-2">Source ID</th>
                <th className="px-4 py-2">Quote Snippet</th>
                <th className="px-4 py-2 text-right">Confidence</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 bg-white">
              {answer.evidence.map((ev, idx) => (
                <tr key={idx} className="hover:bg-slate-50 transition-colors">
                  <td className="px-4 py-2 font-mono text-xs text-blue-600">{ev.source_document_id}</td>
                  <td className="px-4 py-2 italic text-slate-600 truncate max-w-[200px]">"{ev.quote}"</td>
                  <td className="px-4 py-2 text-right font-medium">{(ev.confidence * 100).toFixed(0)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Insights: Contradictions and Gaps */}
      <section className="space-y-4">
        {(answer.contradictions.length > 0 || answer.knowledge_gaps.length > 0) && (
          <div className="flex items-center gap-2 mb-3 text-slate-900 font-bold text-md">
            <AlertTriangle className="w-5 h-5 text-amber-600" />
            Analysis Insights
          </div>
        )}

        {answer.contradictions.map((c, i) => (
          <div key={`cont-${i}`} className="p-4 bg-red-50 border border-red-100 rounded-lg flex gap-3">
            <AlertTriangle className="w-5 h-5 text-red-500 shrink-0" />
            <div>
              <div className="text-sm font-bold text-red-800 mb-1">Contradiction Detected</div>
              <p className="text-sm text-red-700 leading-relaxed">{c}</p>
            </div>
          </div>
        ))}

        {answer.knowledge_gaps.map((gap, i) => (
          <div key={`gap-${i}`} className="p-4 bg-amber-50 border border-amber-100 rounded-lg flex gap-3">
            <InfoIcon className="w-5 h-5 text-amber-600 shrink-0" />
            <div>
              <div className="text-sm font-bold text-amber-800 mb-1">Knowledge Gap</div>
              <p className="text-sm text-amber-700 leading-relaxed">{gap}</p>
            </div>
          </div>
        ))}
      </section>
    </div>
  );
}

// Simple replacement for Info icon since Lucide's Info is named Info
function InfoIcon(props: any) {
  return <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 2-2"/></svg>;
}
