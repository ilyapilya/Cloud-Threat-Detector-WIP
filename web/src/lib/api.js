const BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail ?? `Request failed: ${res.status}`)
  }
  return res.json()
}

// POST /api/v1/scan
// credentials: { access_key_id, secret_access_key, region }
export function createScan(credentials) {
  return request('/api/v1/scan', {
    method: 'POST',
    body: JSON.stringify({ provider: 'aws', credentials }),
  })
}

// GET /api/v1/scan/:id
export function getScan(scanId) {
  return request(`/api/v1/scan/${scanId}`)
}

// GET /api/v1/scan/:id/findings
export function getScanFindings(scanId) {
  return request(`/api/v1/scan/${scanId}/findings`)
}

// ── localStorage scan history ─────────────────────────────────────────────
const HISTORY_KEY = 'cg_recent_scans'
const MAX_HISTORY = 10

export function saveToHistory(scan) {
  try {
    const existing = getHistory()
    const updated = [
      { id: scan.id, createdAt: scan.created_at, provider: scan.provider },
      ...existing.filter(s => s.id !== scan.id),
    ].slice(0, MAX_HISTORY)
    localStorage.setItem(HISTORY_KEY, JSON.stringify(updated))
  } catch {
    // localStorage unavailable — silently skip
  }
}

export function getHistory() {
  try {
    return JSON.parse(localStorage.getItem(HISTORY_KEY) ?? '[]')
  } catch {
    return []
  }
}