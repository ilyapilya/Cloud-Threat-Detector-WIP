import { useState } from 'react'
import { ChevronDown, ChevronUp, Lock } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import RemediationPanel from './RemediationPanel'

const SEVERITY_VARIANT = {
  critical: 'critical',
  high:     'high',
  medium:   'medium',
  low:      'low',
  info:     'secondary',
}

// Free tier: first 5 findings get AI fix. isLocked=true shows the upgrade CTA instead.
export default function FindingCard({ finding, isLocked = false }) {
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
            {finding.region        && <span className="ml-2 text-slate-600">· {finding.region}</span>}
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

          {isLocked ? (
            /* Pro paywall */
            <div className="relative">
              <div className="pointer-events-none select-none rounded-xl border border-slate-700 bg-slate-800/40 p-4 blur-sm">
                <p className="text-sm text-slate-300">Step 1: Go to the AWS Console…</p>
                <p className="mt-2 font-mono text-xs text-green-400">aws s3api put-public-access-block…</p>
              </div>
              <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 rounded-xl bg-slate-950/70 backdrop-blur-sm">
                <Lock className="h-5 w-5 text-slate-400" />
                <p className="text-sm font-medium text-white">AI fixes are a Pro feature</p>
                <Button
                  size="sm"
                  className="bg-cyan-400 text-slate-950 hover:bg-cyan-300"
                  onClick={e => {
                    e.stopPropagation()
                    window.dispatchEvent(new CustomEvent('cloudguard:upgrade'))
                  }}
                >
                  Upgrade to Pro — $29/mo
                </Button>
              </div>
            </div>
          ) : (
            <RemediationPanel finding={finding} />
          )}
        </div>
      )}
    </div>
  )
}
