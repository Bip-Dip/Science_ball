import { API_BASE_URL } from './client';
import { AnswerResponse } from './answers';

export async function exportToMarkdown(answerData: AnswerResponse): Promise<Blob> {
  const response = await fetch(`${API_BASE_URL}/api/v1/exports/markdown`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ answer_data: answerData }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Export failed');
  }

  return await response.blob();
}
