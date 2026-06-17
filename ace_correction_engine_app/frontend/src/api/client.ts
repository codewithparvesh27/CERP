import type { CreateSessionResponse, CorrectionItem } from '../types/models';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

export async function createSession(aceRequestMessage: string, aceResponseMessage: string): Promise<CreateSessionResponse> {
  const res = await fetch(`${API_BASE}/correction-sessions`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ aceRequestMessage, aceResponseMessage })
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function submitCorrection(sessionId: string, itemId: string, newValue: string): Promise<CorrectionItem> {
  const res = await fetch(`${API_BASE}/correction-sessions/${sessionId}/corrections/${itemId}`, {
    method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ newValue })
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function generateRevised(sessionId: string): Promise<{ revisedAceRequestMessage: string; status: string }> {
  const res = await fetch(`${API_BASE}/correction-sessions/${sessionId}/generate`, { method: 'POST' });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
