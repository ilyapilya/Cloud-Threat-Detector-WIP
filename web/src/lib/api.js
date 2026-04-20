const BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

// ── Base fetchers ─────────────────────────────────────────────────────────────

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

async function authRequest(path, getToken, options = {}) {
  const token = await getToken()
  return request(path, {
    ...options,
    headers: { Authorization: `Bearer ${token}`, ...options.headers },
  })
}

// ── Scan API ──────────────────────────────────────────────────────────────────

// POST /api/v1/scan  (getToken optional — passes user_id if signed in)
export async function createScan(credentials, getToken = null) {
  const opts = {
    method: 'POST',
    body: JSON.stringify({ provider: 'aws', credentials }),
  }
  if (getToken) return authRequest('/api/v1/scan', getToken, opts)
  return request('/api/v1/scan', opts)
}

// GET /api/v1/scan/:id
export function getScan(scanId) {
  return request(`/api/v1/scan/${scanId}`)
}

// GET /api/v1/scan/:id/findings
export function getScanFindings(scanId) {
  return request(`/api/v1/scan/${scanId}/findings`)
}

// GET /api/v1/scans  (requires auth)
export function listScans(getToken) {
  return authRequest('/api/v1/scans', getToken)
}

// POST /api/v1/scan/:id/schedule
export function scheduleScan(scanId, email, notify_weekly, getToken) {
  return authRequest(`/api/v1/scan/${scanId}/schedule`, getToken, {
    method: 'POST',
    body: JSON.stringify({ notify_email: email, notify_weekly }),
  })
}

// POST /api/v1/findings/:id/remediate
export function getRemediation(findingId, getToken) {
  return authRequest(`/api/v1/findings/${findingId}/remediate`, getToken, { method: 'POST' })
}

// GET /api/v1/me
export function getMe(getToken) {
  return authRequest('/api/v1/me', getToken)
}

// POST /api/v1/stripe/checkout
export function createCheckout(email, getToken) {
  return authRequest('/api/v1/stripe/checkout', getToken, {
    method: 'POST',
    body: JSON.stringify({ email }),
  })
}

// GET /api/v1/scan/:id/findings (public — for share page)
export function getPublicScanFindings(scanId) {
  return request(`/api/v1/scan/${scanId}/findings`)
}

// ── localStorage scan history (fallback for unauthenticated users) ─────────────
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
