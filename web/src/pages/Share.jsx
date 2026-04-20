import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Helmet } from 'react-helmet-async'
import { Shield, AlertTriangle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import ShareCard from '@/components/scan/ShareCard'
import { getScan, getPublicScanFindings } from '@/lib/api'

export default function Share() {
  const { id: scanId }    = useParams()
  const [scan,     setScan]     = useState(null)
  const [findings, setFindings] = useState([])
  const [loading,  setLoading]  = useState(true)
  const [error,    setError]    = useState(null)

  useEffect(() => {
    if (!scanId) return
    Promise.all([getScan(scanId), getPublicScanFindings(scanId)])
      .then(([s, f]) => {
        if (s.status !== 'completed') throw new Error('Scan not yet complete.')
        setScan(s)
        setFindings(f.findings ?? [])
      })
      .catch(err => setError(err.message))
      .finally(() => setLoading(false))
  }, [scanId])

  const ogTitle       = scan ? `AWS Security Grade: ${scan.grade} (${scan.score}/100) — CloudGuard` : 'CloudGuard Security Report'
  const ogDescription = scan
    ? `This AWS account scored ${scan.score}/100 with grade ${scan.grade}. ${scan.findings_count ?? 0} security findings. See how your account stacks up.`
    : 'Cloud security scanner — 14 AWS checks in under 60 seconds.'
  const ogUrl = typeof window !== 'undefined' ? window.location.href : ''

  return (
    <>
      <Helmet>
        <title>{ogTitle}</title>
        <meta name="description"        content={ogDescription} />
        <meta property="og:title"       content={ogTitle} />
        <meta property="og:description" content={ogDescription} />
        <meta property="og:url"         content={ogUrl} />
        <meta property="og:type"        content="website" />
        <meta name="twitter:card"       content="summary" />
        <meta name="twitter:title"      content={ogTitle} />
        <meta name="twitter:description" content={ogDescription} />
      </Helmet>

      <div className="min-h-screen bg-slate-950">
        {/* Minimal nav — no auth required */}
        <nav className="fixed top-0 z-50 w-full border-b border-slate-800/50 bg-slate-950/90 backdrop-blur-xl">
          <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4 sm:px-6">
            <Link to="/" className="flex items-center gap-2">
              <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-cyan-400/10 ring-1 ring-cyan-400/30">
                <Shield className="h-3.5 w-3.5 text-cyan-400" />
              </div>
              <span className="font-bold text-white tracking-tight">CloudGuard</span>
            </Link>
            <Button asChild size="sm">
              <Link to="/sign-up">Scan yours free →</Link>
            </Button>
          </div>
        </nav>

        <main className="mx-auto max-w-lg px-4 pt-24 pb-16 sm:px-6">
          {loading && (
            <div className="flex justify-center py-20">
              <div className="h-8 w-8 animate-spin rounded-full border-2 border-cyan-400 border-t-transparent" />
            </div>
          )}

          {!loading && error && (
            <div className="flex flex-col items-center gap-4 rounded-2xl border border-red-500/20 bg-red-500/5 py-16 text-center">
              <AlertTriangle className="h-10 w-10 text-red-400" />
              <div>
                <p className="font-semibold text-white">Report not available</p>
                <p className="mt-1 text-sm text-slate-400">{error}</p>
              </div>
              <Button asChild variant="outline">
                <Link to="/">Go home</Link>
              </Button>
            </div>
          )}

          {!loading && !error && scan && (
            <div className="space-y-6">
              <div className="text-center">
                <p className="text-sm text-slate-500">Shared AWS security report</p>
              </div>
              <ShareCard scan={scan} findings={findings} />
            </div>
          )}
        </main>
      </div>
    </>
  )
}
