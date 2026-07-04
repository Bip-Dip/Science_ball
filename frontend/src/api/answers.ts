import { API_BASE_URL } from './client';
import { SearchFilters } from './search';

export interface AnswerOptions {
  include_graph?: boolean;
  include_experts?: boolean;
  include_contradictions?: boolean;
}

export interface EvidenceItem {
  source_document_id: string;
  chunk_id: string;
  quote: string;
  confidence: number;
}

export interface AnswerResponse {
  answer: {
    summary: string;
    confidence: number;
  };
  tables: Array<{
    title: string;
    columns: string[];
    rows: any[][];
  }>;
  evidence: EvidenceItem[];
  contradictions: any[];
  knowledge_gaps: any[];
  experts: any[];
  graph?: {
    nodes: any[];
    edges: any[];
  };
}

export async function getGroundedAnswer(
  query: string,
  filters: SearchFilters = {},
  options: AnswerOptions = {}
): Promise<AnswerResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/answers`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, filters, options }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to generate answer');
  }

  return response.json();
}
