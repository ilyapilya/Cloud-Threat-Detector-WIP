import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Plus, ArrowRight, Shield, Clock } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import AppNav from '@/components/AppNav'
import { getHistory, getScan } from '@/lib/api'

const GRADE_COLOR = {
  A: 'text-green-400',
  B: 'text-cyan-400',
  C: 'text-yellow-400',
  D: 'text-orange-400',
  F: 'text-red-400',
}

function RecentScanRow({ entry }) {
  const [scan, setScan] = useState(null)

  useEffect(() => {
    getScan(entry.id)
      .then(setScan)
      .catch(() => null)
  }, [entry.id])

  const gradeColor = GRADE_COLOR[scan?.grade] ?? 'text-slate-400'

  return (
    <Link
      to={`/scan/${entry.id}`}
      className="flex items-center gap-4 rounded-xl border border-slate-800 bg-slate-900/50 px-5 py-4 transition-colors hover:bg-slate-800/60 hover:border-slate-700"
    >
      {/* Grade */}
      <div className={`w-10 text-center text-2xl font-black ${gradeColor}`}>
        {scan?.grade ?? '—'}
      </div>

      {/* Details */}
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-white">
          {scan?.provider?.toUpperCase() ?? 'AWS'} Scan
        </p>
        <p className="text-xs text-slate-500">
          {new Date(entry.createdAt).toLocaleString()}
        </p>
      </div>

      {/* Status / findings count */}
      <div className="flex items-center gap-3">
        {scan?.status === 'completed' && scan.findings_count != null && (
          <span className="text-sm text-slate-400">{scan.findings_count} findings</span>
        )}
        {scan?.status === 'running' || scan?.status === 'pending' ? (
          <Badge variant="default" className="animate-pulse">Running</Badge>
        ) : scan?.status === 'failed' ? (
          <Badge variant="critical">Failed</Badge>
        ) : null}
        <ArrowRight className="h-4 w-4 text-slate-600" />
      </div>
    </Link>
  )
}

export default function Dashboard() {
  const history = getHistory()

  return (
    <div className="min-h-screen bg-slate-950">
      <AppNav />

      <main className="mx-auto max-w-4xl px-4 pt-24 pb-16 sm:px-6">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">Dashboard</h1>
            <p className="mt-1 text-sm text-slate-400">Your cloud security overview</p>
          </div>
          <Button asChild>
            <Link to="/scan/new">
              <Plus className="h-4 w-4" />
              New Scan
            </Link>
          </Button>
        </div>

        {history.length === 0 ? (
          /* ── Empty state ── */
          <div className="flex flex-col items-center gap-6 rounded-2xl border border-dashed border-slate-700 py-20 text-center">
            <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-slate-900 ring-1 ring-slate-700">
              <Shield className="h-8 w-8 text-slate-600" />
            </div>
            <div>
              <p className="text-lg font-semibold text-white">No scans yet</p>
              <p className="mt-1 text-sm text-slate-400 max-w-xs mx-auto">
                Connect your AWS account to run your first security scan in under 60 seconds.
              </p>
            </div>
            <Button asChild size="lg">
              <Link to="/scan/new">
                Start Free Scan
                <ArrowRight className="h-4 w-4" />
              </Link>
            </Button>
            <p className="text-xs text-slate-600">Read-only access · No agent to install</p>
          </div>
        ) : (
          /* ── Recent scans ── */
          <div>
            <div className="mb-4 flex items-center gap-2 text-xs font-semibold uppercase tracking-widest text-slate-500">
              <Clock className="h-3.5 w-3.5" />
              Recent Scans
            </div>
            <div className="space-y-2">
              {history.map(entry => (
                <RecentScanRow key={entry.id} entry={entry} />
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
