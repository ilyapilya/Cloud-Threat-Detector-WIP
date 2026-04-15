import FindingCard from './FindingCard'

const SEVERITY_ORDER  = { critical: 0, high: 1, medium: 2, low: 3, info: 4 }
const SEVERITY_LABELS = { critical: 'Critical', high: 'High', medium: 'Medium', low: 'Low', info: 'Info' }
const SEVERITY_COLORS = {
  critical: 'text-red-400',
  high:     'text-orange-400',
  medium:   'text-yellow-400',
  low:      'text-blue-400',
  info:     'text-slate-400',
}

// Groups sorted findings by severity for section headers
function groupBySeverity(findings) {
  const sorted = [...findings].sort(
    (a, b) => (SEVERITY_ORDER[a.severity] ?? 5) - (SEVERITY_ORDER[b.severity] ?? 5)
  )
  return sorted.reduce((groups, f) => {
    const key = f.severity
    if (!groups[key]) groups[key] = []
    groups[key].push(f)
    return groups
  }, {})
}

export default function FindingsList({ findings = [], isLocked = false }) {
  if (findings.length === 0) {
    return (
      <div className="flex flex-col items-center gap-3 rounded-xl border border-green-500/20 bg-green-500/5 py-12 text-center">
        <p className="text-2xl">🎉</p>
        <p className="font-semibold text-white">No findings — clean account</p>
        <p className="text-sm text-slate-400">All 14 security checks passed. Keep it that way.</p>
      </div>
    )
  }

  const groups = groupBySeverity(findings)
  const severityKeys = Object.keys(SEVERITY_ORDER).filter(k => groups[k]?.length > 0)

  let cardIndex = 0

  return (
    <div className="space-y-8">
      {severityKeys.map(severity => (
        <div key={severity}>
          {/* Section header */}
          <div className="mb-3 flex items-center gap-3">
            <h3 className={`text-sm font-bold uppercase tracking-widest ${SEVERITY_COLORS[severity]}`}>
              {SEVERITY_LABELS[severity]}
            </h3>
            <span className="text-xs text-slate-500">
              {groups[severity].length} {groups[severity].length === 1 ? 'finding' : 'findings'}
            </span>
            <div className="h-px flex-1 bg-slate-800" />
          </div>

          {/* Finding cards */}
          <div className="space-y-2">
            {groups[severity].map(finding => {
              const idx = cardIndex++
              return (
                <FindingCard
                  key={finding.id}
                  finding={finding}
                  index={idx}
                  isLocked={isLocked}
                />
              )
            })}
          </div>
        </div>
      ))}

      <p className="text-center text-xs text-slate-600">
        {findings.length} total findings · sorted by severity
      </p>
    </div>
  )
}