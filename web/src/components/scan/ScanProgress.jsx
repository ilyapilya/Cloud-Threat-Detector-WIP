import { useEffect, useState } from 'react'
import { Shield, CheckCircle2, Circle } from 'lucide-react'

// Steps mirror the actual check order in aws_checks.py
const STEPS = [
  { label: 'Validating credentials',         doneAt:  1 },
  { label: 'Checking IAM configuration',     doneAt:  6 },
  { label: 'Scanning S3 buckets',            doneAt: 12 },
  { label: 'Analyzing security groups',      doneAt: 20 },
  { label: 'Checking CloudTrail & logging',  doneAt: 30 },
  { label: 'Reviewing encryption settings',  doneAt: 40 },
  { label: 'Generating your report',         doneAt: 999 }, // last — stays active until done
]

export default function ScanProgress({ elapsed = 0 }) {
  return (
    <div className="flex flex-col items-center gap-8 py-12">
      {/* Animated shield */}
      <div className="relative">
        <div className="absolute inset-0 rounded-full bg-cyan-400/10 blur-2xl" />
        <div className="relative flex h-20 w-20 items-center justify-center rounded-2xl border border-cyan-400/20 bg-slate-900">
          <Shield className="h-9 w-9 animate-pulse text-cyan-400" />
        </div>
      </div>

      <div className="text-center">
        <h2 className="text-xl font-semibold text-white">Scanning your AWS environment</h2>
        <p className="mt-1 text-sm text-slate-400">Running 14 security checks — usually under 60 seconds</p>
      </div>

      {/* Step checklist */}
      <div className="w-full max-w-sm space-y-3">
        {STEPS.map(({ label, doneAt }) => {
          const done    = elapsed >= doneAt
          const active  = !done && elapsed >= (doneAt - 10) // show as "in progress" 10s before done

          return (
            <div key={label} className="flex items-center gap-3">
              {done ? (
                <CheckCircle2 className="h-4 w-4 shrink-0 text-green-400" />
              ) : active ? (
                <Circle className="h-4 w-4 shrink-0 animate-pulse text-cyan-400" />
              ) : (
                <Circle className="h-4 w-4 shrink-0 text-slate-700" />
              )}
              <span className={`text-sm ${done ? 'text-slate-400 line-through' : active ? 'text-white' : 'text-slate-600'}`}>
                {label}
              </span>
              {active && (
                <span className="ml-auto text-xs text-cyan-400 animate-pulse">running…</span>
              )}
            </div>
          )
        })}
      </div>

      {elapsed > 0 && (
        <p className="text-xs text-slate-600">{elapsed}s elapsed</p>
      )}
    </div>
  )
}