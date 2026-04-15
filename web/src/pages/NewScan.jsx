import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Shield } from 'lucide-react'
import AppNav from '@/components/AppNav'
import CredentialForm from '@/components/scan/CredentialForm'
import { createScan, saveToHistory } from '@/lib/api'

export default function NewScan() {
  const navigate  = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState(null)

  async function handleSubmit(credentials) {
    setLoading(true)
    setError(null)
    try {
      const scan = await createScan(credentials)
      saveToHistory(scan)
      navigate(`/scan/${scan.id}`)
    } catch (err) {
      setError(err.message)
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-950">
      <AppNav />

      <main className="mx-auto max-w-lg px-4 pt-24 pb-16 sm:px-6">
        {/* Header */}
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl border border-cyan-400/20 bg-cyan-400/5">
            <Shield className="h-7 w-7 text-cyan-400" />
          </div>
          <h1 className="text-2xl font-bold text-white">New AWS Scan</h1>
          <p className="mt-2 text-sm text-slate-400">
            Enter your AWS credentials to scan for security vulnerabilities.
            We run 14 checks in under 60 seconds.
          </p>
        </div>

        {/* Form card */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6">
          <CredentialForm
            onSubmit={handleSubmit}
            loading={loading}
            error={error}
          />
        </div>

        <p className="mt-6 text-center text-xs text-slate-600">
          Need a read-only IAM user?{' '}
          <a
            href="https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html"
            target="_blank"
            rel="noopener noreferrer"
            className="text-cyan-400/70 hover:text-cyan-400 transition-colors"
          >
            AWS docs →
          </a>
        </p>
      </main>
    </div>
  )
}
