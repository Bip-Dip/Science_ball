import { API_BASE_URL } from './client';

export interface SearchFilters {
  practice_region?: 'domestic' | 'foreign';
  year_from?: number;
  year_to?: number;
  min_confidence?: number;
}

export interface SearchResultItem {
  chunk_id: string;
  document_id: string;
  text: string;
  score: number;
  source_type: string;
  year: number;
  geography: string[];
}

export async function searchDocuments(query: string, filters: SearchFilters = {}): Promise<SearchResultItem[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, filters }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Search failed');
  }

  return response.json();
}
