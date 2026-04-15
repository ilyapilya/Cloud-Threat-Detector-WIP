import { useState } from 'react'
import { Eye, EyeOff, ArrowRight, Loader2, ShieldCheck } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

const AWS_REGIONS = [
  'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2',
  'eu-west-1', 'eu-west-2', 'eu-central-1',
  'ap-southeast-1', 'ap-southeast-2', 'ap-northeast-1',
  'ca-central-1', 'sa-east-1',
]

export default function CredentialForm({ onSubmit, loading, error }) {
  const [creds, setCreds] = useState({
    access_key_id:     '',
    secret_access_key: '',
    region:            'us-east-1',
  })
  const [showSecret, setShowSecret] = useState(false)

  function update(field, value) {
    setCreds(prev => ({ ...prev, [field]: value }))
  }

  function handleSubmit(e) {
    e.preventDefault()
    onSubmit(creds)
  }

  const canSubmit = creds.access_key_id.length >= 16 && creds.secret_access_key.length > 0

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {/* Access Key ID */}
      <div className="space-y-1.5">
        <label className="text-sm font-medium text-slate-300">
          AWS Access Key ID
        </label>
        <Input
          type="text"
          placeholder="AKIAIOSFODNN7EXAMPLE"
          value={creds.access_key_id}
          onChange={e => update('access_key_id', e.target.value)}
          className="font-mono"
          autoComplete="off"
          autoCapitalize="off"
          spellCheck={false}
          required
        />
      </div>

      {/* Secret Access Key */}
      <div className="space-y-1.5">
        <label className="text-sm font-medium text-slate-300">
          AWS Secret Access Key
        </label>
        <div className="relative">
          <Input
            type={showSecret ? 'text' : 'password'}
            placeholder="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
            value={creds.secret_access_key}
            onChange={e => update('secret_access_key', e.target.value)}
            className="pr-10 font-mono"
            autoComplete="off"
            spellCheck={false}
            required
          />
          <button
            type="button"
            onClick={() => setShowSecret(s => !s)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors"
            tabIndex={-1}
          >
            {showSecret ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          </button>
        </div>
      </div>

      {/* Region */}
      <div className="space-y-1.5">
        <label className="text-sm font-medium text-slate-300">
          Primary Region
        </label>
        <select
          value={creds.region}
          onChange={e => update('region', e.target.value)}
          className="flex h-10 w-full rounded-lg border border-slate-700 bg-slate-800/50 px-4 py-2 text-sm text-slate-100 focus:border-cyan-500 focus:outline-none focus:ring-1 focus:ring-cyan-500/40"
        >
          {AWS_REGIONS.map(r => (
            <option key={r} value={r}>{r}</option>
          ))}
        </select>
      </div>

      {/* Error */}
      {error && (
        <div className="rounded-lg border border-red-500/20 bg-red-500/5 px-4 py-3 text-sm text-red-400">
          {error}
        </div>
      )}

      {/* Trust note */}
      <div className="flex items-start gap-2 rounded-lg border border-slate-700/50 bg-slate-800/30 px-4 py-3">
        <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-cyan-400/70" />
        <p className="text-xs text-slate-400 leading-relaxed">
          Credentials are sent over HTTPS directly to our API, validated once, and never stored.
          Use a{' '}
          <span className="text-slate-300">read-only IAM user</span>
          {' '}with SecurityAudit policy for best practice.
        </p>
      </div>

      <Button type="submit" size="lg" className="w-full" disabled={!canSubmit || loading}>
        {loading ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin" />
            Starting scan...
          </>
        ) : (
          <>
            Start Security Scan
            <ArrowRight className="h-4 w-4" />
          </>
        )}
      </Button>
    </form>
  )
}