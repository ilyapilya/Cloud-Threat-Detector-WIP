import { ArrowRight, CheckCircle2 } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Button } from '../ui/button'
import WaitlistForm from './WaitlistForm'

const clerkConfigured = !!import.meta.env.VITE_CLERK_PUBLISHABLE_KEY

const trustBadges = [
  'Read-only access — we never write to your cloud',
  'No agent to install',
  '60-second setup',
]

export default function Hero() {
  return (
    <section className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden px-4 pt-16">
      {/* Background gradient */}
      <div className="pointer-events-none absolute inset-0 -z-10">
        <div className="absolute inset-0 bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950" />
        <div className="absolute left-1/2 top-1/3 h-[600px] w-[600px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-cyan-500/5 blur-3xl" />
        <div className="absolute right-1/4 top-1/2 h-[400px] w-[400px] -translate-y-1/2 rounded-full bg-blue-500/5 blur-3xl" />
      </div>

      <div className="mx-auto max-w-4xl text-center animate-fade-in">
        {/* Eyebrow badge */}
        <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/5 px-4 py-1.5 text-sm text-cyan-400">
          <span className="h-1.5 w-1.5 rounded-full bg-cyan-400 animate-pulse" />
          AI-Powered Cloud Security Scanner
        </div>

        {/* Headline */}
        <h1 className="mb-6 text-4xl font-extrabold leading-tight tracking-tight text-white sm:text-5xl lg:text-6xl">
          Stop Cloud Misconfigurations{' '}
          <span className="bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">Before Attackers Do</span>
        </h1>

        {/* Subheadline */}
        <p className="mx-auto mb-10 max-w-2xl text-lg text-slate-400 leading-relaxed">
          CloudGuard automatically scans your AWS infrastructure for security vulnerabilities
          and generates AI-powered fix instructions — in under 60 seconds.
        </p>

        {/* CTA */}
        <div className="flex flex-col items-center gap-6">
          {clerkConfigured ? (
            <div className="flex flex-col items-center gap-4 sm:flex-row">
              <Button size="xl" asChild>
                <Link to="/sign-up">
                  Start Free Scan
                  <ArrowRight className="h-5 w-5" />
                </Link>
              </Button>
              <Button size="xl" variant="outline" asChild>
                <a href="#how-it-works">See How It Works</a>
              </Button>
            </div>
          ) : (
            <div id="waitlist" className="w-full max-w-md">
              <WaitlistForm />
            </div>
          )}

          {/* Trust badges */}
          <div className="flex flex-wrap justify-center gap-x-6 gap-y-2">
            {trustBadges.map((badge) => (
              <div key={badge} className="flex items-center gap-1.5 text-sm text-slate-500">
                <CheckCircle2 className="h-3.5 w-3.5 text-cyan-500/70" />
                {badge}
              </div>
            ))}
          </div>
        </div>

        {/* Mock scan card — visual anchor */}
        <div className="mx-auto mt-16 max-w-2xl rounded-xl border border-slate-800 bg-slate-900/60 p-4 text-left backdrop-blur-sm glow-cyan">
          <div className="mb-3 flex items-center gap-2">
            <div className="h-3 w-3 rounded-full bg-red-500/80" />
            <div className="h-3 w-3 rounded-full bg-yellow-500/80" />
            <div className="h-3 w-3 rounded-full bg-green-500/80" />
            <span className="ml-2 text-xs text-slate-500 font-mono">scan_results.json</span>
          </div>
          <div className="space-y-2 font-mono text-xs">
            <div className="flex items-center justify-between rounded-lg border border-red-500/20 bg-red-500/5 px-3 py-2">
              <span className="text-red-400">CRITICAL</span>
              <span className="text-slate-300">S3 bucket publicly accessible — s3://prod-backups</span>
            </div>
            <div className="flex items-center justify-between rounded-lg border border-orange-500/20 bg-orange-500/5 px-3 py-2">
              <span className="text-orange-400">HIGH</span>
              <span className="text-slate-300">Security group 0.0.0.0/0 open on port 22 (SSH)</span>
            </div>
            <div className="flex items-center justify-between rounded-lg border border-yellow-500/20 bg-yellow-500/5 px-3 py-2">
              <span className="text-yellow-400">MEDIUM</span>
              <span className="text-slate-300">CloudTrail logging disabled in us-east-1</span>
            </div>
            <div className="flex items-center justify-between rounded-lg border border-slate-700 bg-slate-800/40 px-3 py-1.5 text-slate-500">
              <span>+12 more findings</span>
              <span className="text-cyan-400">Upgrade to see all →</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
