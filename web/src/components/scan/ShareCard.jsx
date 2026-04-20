import { Link } from 'react-router-dom'
import { Shield, ArrowRight } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

const GRADE_STYLE = {
  A: { text: 'text-green-400',  glow: 'shadow-green-400/20',  border: 'border-green-400/20',  bg: 'bg-green-400/5'  },
  B: { text: 'text-cyan-400',   glow: 'shadow-cyan-400/20',   border: 'border-cyan-400/20',   bg: 'bg-cyan-400/5'   },
  C: { text: 'text-yellow-400', glow: 'shadow-yellow-400/20', border: 'border-yellow-400/20', bg: 'bg-yellow-400/5' },
  D: { text: 'text-orange-400', glow: 'shadow-orange-400/20', border: 'border-orange-400/20', bg: 'bg-orange-400/5' },
  F: { text: 'text-red-400',    glow: 'shadow-red-400/20',    border: 'border-red-400/20',    bg: 'bg-red-400/5'    },
}

const SEVERITY_VARIANT = { critical: 'critical', high: 'high', medium: 'medium', low: 'low' }

export default function ShareCard({ scan, findings = [] }) {
  const style    = GRADE_STYLE[scan.grade] ?? GRADE_STYLE['F']
  const top3     = findings.slice(0, 3)
  const scanDate = new Date(scan.created_at).toLocaleDateString('en-US', {
    month: 'long', day: 'numeric', year: 'numeric',
  })

  return (
    <div className={`rounded-2xl border ${style.border} ${style.bg} p-8`}>
      {/* Brand */}
      <div className="mb-6 flex items-center gap-2">
        <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-cyan-400/10 ring-1 ring-cyan-400/30">
          <Shield className="h-3.5 w-3.5 text-cyan-400" />
        </div>
        <span className="font-bold text-white tracking-tight">CloudGuard</span>
        <span className="ml-auto text-xs text-slate-500">{scanDate}</span>
      </div>

      {/* Score */}
      <div className="mb-6 flex items-end gap-4">
        <div className={`text-8xl font-black leading-none ${style.text}`}>
          {scan.grade ?? '?'}
        </div>
        <div className="mb-2">
          <p className="text-2xl font-bold text-white">{scan.score ?? 0}/100</p>
          <p className="text-sm text-slate-400">security score</p>
        </div>
      </div>

      {/* Top findings */}
      {top3.length > 0 && (
        <div className="mb-6 space-y-2">
          <p className="mb-3 text-xs font-semibold uppercase tracking-widest text-slate-500">
            Top Findings
          </p>
          {top3.map(f => (
            <div key={f.id} className="flex items-center gap-2">
              <Badge variant={SEVERITY_VARIANT[f.severity] ?? 'secondary'} className="capitalize shrink-0 text-xs">
                {f.severity}
              </Badge>
              <span className="text-sm text-slate-300 truncate">{f.title}</span>
            </div>
          ))}
          {scan.findings_count > 3 && (
            <p className="text-xs text-slate-500">+{scan.findings_count - 3} more findings</p>
          )}
        </div>
      )}

      {/* CTA */}
      <div className="rounded-xl border border-slate-700 bg-slate-900/60 p-4 text-center">
        <p className="mb-3 text-sm text-slate-300">
          How secure is <span className="font-semibold text-white">your</span> AWS account?
        </p>
        <Button asChild className="w-full">
          <Link to="/sign-up">
            Scan yours free — 14 checks in 60s
            <ArrowRight className="h-4 w-4" />
          </Link>
        </Button>
        <p className="mt-2 text-xs text-slate-600">No credit card · Read-only access</p>
      </div>
    </div>
  )
}
