import { Badge } from '@/components/ui/badge'

const GRADE_CONFIG = {
  A: { color: 'text-green-400',  glow: 'shadow-green-400/20',  bg: 'bg-green-400/5',  border: 'border-green-400/20' },
  B: { color: 'text-cyan-400',   glow: 'shadow-cyan-400/20',   bg: 'bg-cyan-400/5',   border: 'border-cyan-400/20'  },
  C: { color: 'text-yellow-400', glow: 'shadow-yellow-400/20', bg: 'bg-yellow-400/5', border: 'border-yellow-400/20'},
  D: { color: 'text-orange-400', glow: 'shadow-orange-400/20', bg: 'bg-orange-400/5', border: 'border-orange-400/20'},
  F: { color: 'text-red-400',    glow: 'shadow-red-400/20',    bg: 'bg-red-400/5',    border: 'border-red-400/20'  },
}

const SEVERITY_BADGE = {
  critical: 'critical',
  high:     'high',
  medium:   'medium',
  low:      'low',
}

function countBySeverity(findings) {
  return findings.reduce((acc, f) => {
    acc[f.severity] = (acc[f.severity] ?? 0) + 1
    return acc
  }, {})
}

export default function ScoreCard({ scan, findings = [] }) {
  const grade  = scan.grade ?? 'F'
  const score  = scan.score ?? 0
  const cfg    = GRADE_CONFIG[grade] ?? GRADE_CONFIG.F
  const counts = countBySeverity(findings)

  const pills = [
    { label: 'Critical', key: 'critical', variant: 'critical' },
    { label: 'High',     key: 'high',     variant: 'high'     },
    { label: 'Medium',   key: 'medium',   variant: 'medium'   },
    { label: 'Low',      key: 'low',      variant: 'low'      },
  ].filter(p => counts[p.key] > 0)

  return (
    <div className={`rounded-2xl border ${cfg.border} ${cfg.bg} p-6 shadow-2xl ${cfg.glow}`}>
      <div className="flex flex-col gap-6 sm:flex-row sm:items-center sm:gap-8">
        {/* Grade */}
        <div className="flex items-center gap-4">
          <div className={`text-8xl font-black leading-none ${cfg.color} drop-shadow-lg`}>
            {grade}
          </div>
          <div>
            <p className="text-3xl font-bold text-white">{score}<span className="text-lg text-slate-400"> / 100</span></p>
            <p className="text-sm text-slate-400 mt-0.5">Security Score</p>
          </div>
        </div>

        {/* Divider */}
        <div className="hidden h-16 w-px bg-slate-700 sm:block" />

        {/* Severity breakdown */}
        <div className="flex-1">
          <p className="mb-3 text-xs font-semibold uppercase tracking-widest text-slate-500">
            Findings breakdown
          </p>
          {pills.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {pills.map(p => (
                <Badge key={p.key} variant={p.variant} className="px-3 py-1 text-sm">
                  {counts[p.key]} {p.label}
                </Badge>
              ))}
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Badge variant="success" className="px-3 py-1 text-sm">No issues found</Badge>
              <span className="text-sm text-slate-400">Your account is clean.</span>
            </div>
          )}
        </div>
      </div>

      {/* Footer meta */}
      <div className="mt-4 flex flex-wrap items-center gap-4 border-t border-slate-700/50 pt-4 text-xs text-slate-500">
        <span>Provider: <span className="text-slate-300 uppercase">{scan.provider}</span></span>
        <span>Scanned: <span className="text-slate-300">{new Date(scan.completed_at ?? scan.created_at).toLocaleString()}</span></span>
        <span>Checks run: <span className="text-slate-300">14</span></span>
        <span className="ml-auto text-slate-600">ID: {String(scan.id).slice(0, 8)}…</span>
      </div>
    </div>
  )
}