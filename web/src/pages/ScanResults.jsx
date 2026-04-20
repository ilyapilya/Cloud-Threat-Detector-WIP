import { useEffect, useRef, useState, useCallback } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useAuth, useUser } from '@clerk/clerk-react'
import { AlertTriangle, ArrowLeft, RefreshCw, Share2 } from 'lucide-react'
import AppNav from '@/components/AppNav'
import ScanProgress from '@/components/scan/ScanProgress'
import ScoreCard from '@/components/scan/ScoreCard'
import FindingsList from '@/components/scan/FindingsList'
import { Button } from '@/components/ui/button'
import { getScan, getScanFindings, getMe, createCheckout } from '@/lib/api'

const POLL_INTERVAL_MS = 2000
const TIMEOUT_S        = 120

export default function ScanResults() {
  const { id: scanId }   = useParams()
  const { getToken }     = useAuth()
  const { user }         = useUser()

  const [scan,     setScan]     = useState(null)
  const [findings, setFindings] = useState([])
  const [elapsed,  setElapsed]  = useState(0)
  const [timedOut, setTimedOut] = useState(false)
  const [error,    setError]    = useState(null)
  const [isPro,    setIsPro]    = useState(false)
  const [upgrading, setUpgrading] = useState(false)

  const intervalRef = useRef(null)
  const elapsedRef  = useRef(0)

  async function loadFindings(currentScan) {
    try {
      const data = await getScanFindings(currentScan.id)
      setFindings(data.findings ?? [])
    } catch (err) {
      setError(`Failed to load findings: ${err.message}`)
    }
  }

  function stopPolling() {
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
  }

  // Fetch user plan
  useEffect(() => {
    getMe(getToken)
      .then(data => setIsPro(data.plan === 'pro'))
      .catch(() => {})
  }, [getToken])

  // Listen for upgrade events dispatched from FindingCard paywall CTA
  const handleUpgrade = useCallback(async () => {
    if (!user?.primaryEmailAddress?.emailAddress) return
    setUpgrading(true)
    try {
      const { url } = await createCheckout(user.primaryEmailAddress.emailAddress, getToken)
      window.location.href = url
    } catch (err) {
      alert(`Checkout error: ${err.message}`)
      setUpgrading(false)
    }
  }, [getToken, user])

  useEffect(() => {
    window.addEventListener('cloudguard:upgrade', handleUpgrade)
    return () => window.removeEventListener('cloudguard:upgrade', handleUpgrade)
  }, [handleUpgrade])

  useEffect(() => {
    if (!scanId) return

    getScan(scanId)
      .then(async initial => {
        setScan(initial)
        if (initial.status === 'completed') {
          await loadFindings(initial)
        } else if (initial.status === 'failed') {
          setError(initial.error_msg ?? 'Scan failed.')
        } else {
          intervalRef.current = setInterval(async () => {
            elapsedRef.current += POLL_INTERVAL_MS / 1000
            setElapsed(elapsedRef.current)

            if (elapsedRef.current >= TIMEOUT_S) {
              stopPolling()
              setTimedOut(true)
              return
            }

            try {
              const updated = await getScan(scanId)
              setScan(updated)
              if (updated.status === 'completed') {
                stopPolling()
                await loadFindings(updated)
              } else if (updated.status === 'failed') {
                stopPolling()
                setError(updated.error_msg ?? 'Scan failed.')
              }
            } catch (err) {
              console.warn('Poll error:', err.message)
            }
          }, POLL_INTERVAL_MS)
        }
      })
      .catch(err => setError(err.message))

    return stopPolling
  }, [scanId])

  const isPolling = scan && (scan.status === 'pending' || scan.status === 'running')
  const shareUrl  = `${window.location.origin}/share/${scanId}`

  return (
    <div className="min-h-screen bg-slate-950">
      <AppNav />

      {/* Upgrade overlay */}
      {upgrading && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm">
          <div className="flex flex-col items-center gap-3 text-white">
            <div className="h-8 w-8 animate-spin rounded-full border-2 border-cyan-400 border-t-transparent" />
            <p className="text-sm text-slate-400">Redirecting to checkout…</p>
          </div>
        </div>
      )}

      <main className="mx-auto max-w-4xl px-4 pt-20 pb-16 sm:px-6">
        {/* Back link */}
        <Link
          to="/dashboard"
          className="mb-6 inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-white transition-colors"
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          Dashboard
        </Link>

        {/* Error state */}
        {error && (
          <div className="flex flex-col items-center gap-4 rounded-2xl border border-red-500/20 bg-red-500/5 py-16 text-center">
            <AlertTriangle className="h-10 w-10 text-red-400" />
            <div>
              <p className="font-semibold text-white">Scan failed</p>
              <p className="mt-1 text-sm text-red-400 max-w-md mx-auto">{error}</p>
            </div>
            <Button variant="outline" asChild>
              <Link to="/scan/new">Try again</Link>
            </Button>
          </div>
        )}

        {/* Timeout state */}
        {!error && timedOut && (
          <div className="flex flex-col items-center gap-4 rounded-2xl border border-yellow-500/20 bg-yellow-500/5 py-16 text-center">
            <RefreshCw className="h-10 w-10 text-yellow-400" />
            <div>
              <p className="font-semibold text-white">Taking longer than expected</p>
              <p className="mt-1 text-sm text-slate-400">
                The scan is still running. Refresh the page to check again.
              </p>
            </div>
            <Button variant="outline" onClick={() => window.location.reload()}>
              <RefreshCw className="h-4 w-4" />
              Refresh
            </Button>
          </div>
        )}

        {/* Polling / progress state */}
        {!error && !timedOut && isPolling && (
          <ScanProgress elapsed={elapsed} />
        )}

        {/* Completed state */}
        {!error && !timedOut && scan?.status === 'completed' && (
          <div className="space-y-8">
            <div>
              <div className="mb-4 flex items-center justify-between">
                <h1 className="text-2xl font-bold text-white">Scan Results</h1>
                <Button
                  variant="outline"
                  size="sm"
                  className="gap-1.5 text-slate-400"
                  onClick={() => {
                    navigator.clipboard.writeText(shareUrl)
                    alert('Share link copied!')
                  }}
                >
                  <Share2 className="h-3.5 w-3.5" />
                  Share
                </Button>
              </div>
              <ScoreCard scan={scan} findings={findings} />
            </div>

            <div>
              <h2 className="mb-4 text-lg font-semibold text-white">
                Findings
                {findings.length > 0 && (
                  <span className="ml-2 text-sm font-normal text-slate-400">
                    ({findings.length} total)
                  </span>
                )}
              </h2>
              <FindingsList findings={findings} isPro={isPro} />
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
