import { useState } from 'react'
import { ChevronDown, ChevronUp, Wand2, Lock } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

const SEVERITY_ORDER = { critical: 0, high: 1, medium: 2, low: 3, info: 4 }

// Maps severity → Badge variant (matches our badge.jsx)
const SEVERITY_VARIANT = {
  critical: 'critical',
  high:     'high',
  medium:   'medium',
  low:      'low',
  info:     'secondary',
}

export default function FindingCard({ finding, index, isLocked = false }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div
      className={cn(
        'rounded-xl border bg-slate-900/60 transition-all duration-200',
        finding.severity === 'critical' ? 'border-red-500/20'    :
        finding.severity === 'high'     ? 'border-orange-500/20' :
        finding.severity === 'medium'   ? 'border-yellow-500/20' :
                                          'border-slate-700/60'
      )}
    >
      {/* Main row */}
      <button
        className="flex w-full items-start gap-3 p-4 text-left"
        onClick={() => setExpanded(e => !e)}
      >
        <Badge variant={SEVERITY_VARIANT[finding.severity] ?? 'secondary'} className="mt-0.5 shrink-0 capitalize">
          {finding.severity}
        </Badge>

        <div className="min-w-0 flex-1">
          <p className="font-medium text-white leading-snug">{finding.title}</p>
          <p className="mt-1 font-mono text-xs text-slate-500 truncate">
            {finding.resource_id}
            {finding.resource_type && <span className="ml-2 text-slate-600">· {finding.resource_type}</span>}
            {finding.region       && <span className="ml-2 text-slate-600">· {finding.region}</span>}
          </p>
        </div>

        <div className="ml-2 shrink-0 text-slate-500">
          {expanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
        </div>
      </button>

      {/* Expanded content */}
      {expanded && (
        <div className="border-t border-slate-700/50 px-4 pb-4 pt-3">
          {finding.description && (
            <p className="mb-4 text-sm text-slate-300 leading-relaxed">{finding.description}</p>
          )}

          {/* AI Fix button — stub, locked until Day 5 */}
          {isLocked ? (
            <div className="flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-800/40 px-4 py-2.5">
              <Lock className="h-4 w-4 text-slate-500" />
              <span className="text-sm text-slate-500">AI remediation available on</span>
              <span className="text-sm font-semibold text-cyan-400">Pro</span>
            </div>
          ) : (
            <Button
              variant="outline"
              size="sm"
              className="gap-2 border-cyan-500/30 text-cyan-400 hover:bg-cyan-400/5 hover:border-cyan-400/50"
              disabled
            >
              <Wand2 className="h-3.5 w-3.5" />
              Show AI Fix
              <span className="rounded-full bg-cyan-400/10 px-1.5 py-0.5 text-[10px] font-semibold text-cyan-400">
                Coming Day 5
              </span>
            </Button>
          )}
        </div>
      )}
    </div>
  )
}