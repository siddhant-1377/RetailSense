import type {
  AssociationResult,
  ClusteringResult,
  ComparisonResponse,
  ClassificationModelResult,
  Profile,
  RegressionResult,
  SummaryResponse,
} from './types';

export const API_BASE = import.meta.env.VITE_API_URL || '/api';

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${url}`, options);
  const data = await response.json().catch(() => ({ detail: 'Unexpected server response.' }));
  if (!response.ok) throw new Error(data.detail || 'Request failed.');
  return data as T;
}

export const api = {
  health: () => request<{ status: string }>('/health'),
  summary: (sessionId: string) => request<SummaryResponse>(`/summary?session_id=${encodeURIComponent(sessionId)}`),
  demo: () => request<SummaryResponse>('/demo'),
  upload: (file: File) => {
    const form = new FormData();
    form.append('file', file);
    return request<{ session_id: string; file_name: string; profile: Profile; demo: boolean; preview: Record<string, unknown>[] }>('/upload', { method: 'POST', body: form });
  },
  reset: (sessionId: string) => request<{ session_id: string }>('/reset?session_id=' + encodeURIComponent(sessionId), { method: 'POST' }),
  preprocess: (body: unknown) => request<{ summary: Record<string, number>; outliers: any[]; profile: Profile; message: string }>('/preprocess', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }),
  association: (body: unknown) => request<AssociationResult>('/association', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }),
  classification: (body: unknown) => request<{ j48: ClassificationModelResult; naive_bayes: ClassificationModelResult; comparison: ClassificationModelResult[] }>('/classification', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }),
  regression: (body: unknown) => request<RegressionResult>('/regression', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }),
  regressionPredict: (body: unknown) => request<{ prediction: number; target: string; features: string[] }>('/regression/predict', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }),
  clustering: (body: unknown) => request<ClusteringResult>('/clustering', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }),
  comparison: (sessionId: string) => request<ComparisonResponse>('/comparison?session_id=' + encodeURIComponent(sessionId), { method: 'POST' }),
  insights: (sessionId: string) => request<{ insights: string[]; data_quality: Profile }>(`/insights?session_id=${encodeURIComponent(sessionId)}`),
  dwm: () => request<any>('/dwm'),
  cleanCsvUrl: (sessionId: string) => `${API_BASE}/download/clean?session_id=${encodeURIComponent(sessionId)}`,
};
