import { Link } from 'react-router-dom'
import { ArrowRight } from 'lucide-react'
import { Badge } from '@/components/ui/badge'

const GRADE_STYLE = {
  A: { text: 'text-green-400',  ring: 'ring-green-400/20',  bg: 'bg-green-400/5'  },
  B: { text: 'text-cyan-400',   ring: 'ring-cyan-400/20',   bg: 'bg-cyan-400/5'   },
  C: { text: 'text-yellow-400', ring: 'ring-yellow-400/20', bg: 'bg-yellow-400/5' },
  D: { text: 'text-orange-400', ring: 'ring-orange-400/20', bg: 'bg-orange-400/5' },
  F: { text: 'text-red-400',    ring: 'ring-red-400/20',    bg: 'bg-red-400/5'    },
}

export default function HistoryCard({ scan }) {
  const style = GRADE_STYLE[scan.grade] ?? { text: 'text-slate-400', ring: 'ring-slate-700', bg: 'bg-slate-900' }

  return (
    <Link
      to={`/scan/${scan.id}`}
      className="flex items-center gap-4 rounded-xl border border-slate-800 bg-slate-900/50 px-5 py-4 transition-colors hover:bg-slate-800/60 hover:border-slate-700"
    >
      {/* Grade bubble */}
      <div className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-xl ring-1 ${style.ring} ${style.bg}`}>
        <span className={`text-2xl font-black ${style.text}`}>
          {scan.grade ?? '—'}
        </span>
      </div>

      {/* Meta */}
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-white">
          {scan.provider?.toUpperCase() ?? 'AWS'} Scan
          {scan.score != null && (
            <span className="ml-2 text-xs font-normal text-slate-500">
              {scan.score}/100
            </span>
          )}
        </p>
        <p className="text-xs text-slate-500 mt-0.5">
          {new Date(scan.created_at).toLocaleString()}
        </p>
      </div>

      {/* Right side */}
      <div className="flex items-center gap-3 shrink-0">
        {scan.status === 'completed' && scan.findings_count != null && (
          <span className="text-sm text-slate-400">{scan.findings_count} findings</span>
        )}
        {(scan.status === 'running' || scan.status === 'pending') && (
          <Badge variant="default" className="animate-pulse">Running</Badge>
        )}
        {scan.status === 'failed' && (
          <Badge variant="critical">Failed</Badge>
        )}
        <ArrowRight className="h-4 w-4 text-slate-600" />
      </div>
    </Link>
  )
}
