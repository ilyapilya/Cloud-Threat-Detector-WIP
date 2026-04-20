import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '@clerk/clerk-react'
import { ArrowLeft, Shield } from 'lucide-react'
import { Button } from '@/components/ui/button'
import AppNav from '@/components/AppNav'
import HistoryCard from '@/components/scan/HistoryCard'
import GradeTimeline from '@/components/scan/GradeTimeline'
import { listScans } from '@/lib/api'

export default function History() {
  const { getToken }          = useAuth()
  const [scans,   setScans]   = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    listScans(getToken)
      .then(data => setScans(data.scans ?? []))
      .catch(() => setScans([]))
      .finally(() => setLoading(false))
  }, [getToken])

  const completedScans = scans.filter(s => s.status === 'completed')

  return (
    <div className="min-h-screen bg-slate-950">
      <AppNav />

      <main className="mx-auto max-w-4xl px-4 pt-20 pb-16 sm:px-6">
        {/* Back link */}
        <Link
          to="/dashboard"
          className="mb-6 inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-white transition-colors"
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          Dashboard
        </Link>

        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">Scan History</h1>
            <p className="mt-1 text-sm text-slate-400">
              All your past AWS security scans
            </p>
          </div>
          <Button asChild>
            <Link to="/scan/new">New Scan</Link>
          </Button>
        </div>

        {loading ? (
          <div className="space-y-2">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="h-16 rounded-xl border border-slate-800 bg-slate-900/50 animate-pulse" />
            ))}
          </div>
        ) : scans.length === 0 ? (
          <div className="flex flex-col items-center gap-6 rounded-2xl border border-dashed border-slate-700 py-20 text-center">
            <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-slate-900 ring-1 ring-slate-700">
              <Shield className="h-8 w-8 text-slate-600" />
            </div>
            <div>
              <p className="text-lg font-semibold text-white">No scans yet</p>
              <p className="mt-1 text-sm text-slate-400 max-w-xs mx-auto">
                Run your first scan to start tracking your security posture over time.
              </p>
            </div>
            <Button asChild size="lg">
              <Link to="/scan/new">Start Free Scan</Link>
            </Button>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Grade sparkline — only show if 2+ completed scans */}
            {completedScans.length >= 2 && (
              <GradeTimeline scans={scans} />
            )}

            {/* Full scan list */}
            <div>
              <p className="mb-3 text-xs font-semibold uppercase tracking-widest text-slate-500">
                {scans.length} scan{scans.length !== 1 ? 's' : ''} total
              </p>
              <div className="space-y-2">
                {scans.map(scan => (
                  <HistoryCard key={scan.id} scan={scan} />
                ))}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
