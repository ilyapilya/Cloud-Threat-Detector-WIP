import { useState } from 'react'
import { useAuth } from '@clerk/clerk-react'
import { Wand2, Copy, Check, Terminal, List, AlertTriangle, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { getRemediation } from '@/lib/api'

const RISK_VARIANT = { low: 'low', medium: 'medium', high: 'high', critical: 'critical' }
const RISK_LABEL   = { low: 'Low risk to apply', medium: 'Medium risk', high: 'Review carefully' }

function CopyButton({ text }) {
  const [copied, setCopied] = useState(false)
  function copy() {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }
  return (
    <button
      onClick={copy}
      className="flex items-center gap-1 rounded px-2 py-0.5 text-xs text-slate-400 hover:text-white transition-colors"
    >
      {copied ? <Check className="h-3 w-3 text-green-400" /> : <Copy className="h-3 w-3" />}
      {copied ? 'Copied' : 'Copy'}
    </button>
  )
}

export default function RemediationPanel({ finding }) {
  const { getToken }              = useAuth()
  const [state,    setState]      = useState('idle')   // idle | loading | done | error
  const [result,   setResult]     = useState(null)
  const [errorMsg, setErrorMsg]   = useState('')

  async function fetchFix() {
    setState('loading')
    try {
      const data = await getRemediation(finding.id, getToken)
      setResult(data)
      setState('done')
    } catch (err) {
      setErrorMsg(err.message)
      setState('error')
    }
  }

  if (state === 'idle') {
    return (
      <Button
        variant="outline"
        size="sm"
        className="gap-2 border-cyan-500/30 text-cyan-400 hover:bg-cyan-400/5 hover:border-cyan-400/50"
        onClick={fetchFix}
      >
        <Wand2 className="h-3.5 w-3.5" />
        Show AI Fix
      </Button>
    )
  }

  if (state === 'loading') {
    return (
      <div className="flex items-center gap-2 text-sm text-slate-400">
        <Loader2 className="h-4 w-4 animate-spin text-cyan-400" />
        Generating fix…
      </div>
    )
  }

  if (state === 'error') {
    return (
      <div className="flex items-center gap-2 rounded-lg border border-red-500/20 bg-red-500/5 px-3 py-2 text-sm text-red-400">
        <AlertTriangle className="h-4 w-4 shrink-0" />
        {errorMsg || 'Failed to generate fix. Try again.'}
      </div>
    )
  }

  // state === 'done'
  return (
    <div className="mt-1 space-y-4 rounded-xl border border-cyan-500/20 bg-cyan-500/5 p-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Wand2 className="h-4 w-4 text-cyan-400" />
          <span className="text-sm font-semibold text-white">AI Fix</span>
        </div>
        {result.risk_level && (
          <Badge variant={RISK_VARIANT[result.risk_level] ?? 'secondary'} className="capitalize text-xs">
            {RISK_LABEL[result.risk_level] ?? result.risk_level}
          </Badge>
        )}
      </div>

      {/* Explanation */}
      {result.explanation && (
        <p className="text-sm text-slate-300 leading-relaxed">{result.explanation}</p>
      )}

      {/* CLI command */}
      {result.cli_command && result.cli_command !== 'N/A' && (
        <div>
          <div className="mb-1.5 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-widest text-slate-500">
            <Terminal className="h-3 w-3" />
            CLI Command
          </div>
          <div className="flex items-start justify-between gap-2 rounded-lg bg-slate-950 px-3 py-2.5 font-mono text-xs text-green-400">
            <code className="break-all">{result.cli_command}</code>
            <CopyButton text={result.cli_command} />
          </div>
        </div>
      )}

      {/* Console steps */}
      {result.console_steps?.length > 0 && (
        <div>
          <div className="mb-1.5 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-widest text-slate-500">
            <List className="h-3 w-3" />
            Console Steps
          </div>
          <ol className="space-y-1.5">
            {result.console_steps.map((step, i) => (
              <li key={i} className="flex gap-2 text-sm text-slate-300">
                <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-slate-800 text-xs font-bold text-slate-400">
                  {i + 1}
                </span>
                {step}
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  )
}
