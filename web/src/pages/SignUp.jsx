import { Shield } from 'lucide-react'
import { Link } from 'react-router-dom'
import { SignUp } from '@clerk/clerk-react'

const CLERK_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY

export default function SignUpPage() {
  if (!CLERK_KEY) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center bg-slate-950 px-4">
        <div className="w-full max-w-sm rounded-xl border border-slate-800 bg-slate-900 p-8 text-center">
          <Shield className="mx-auto mb-4 h-10 w-10 text-cyan-400" />
          <h1 className="mb-2 text-xl font-bold text-white">Auth Not Configured</h1>
          <p className="mb-4 text-sm text-slate-400">
            Add{' '}
            <code className="rounded bg-slate-800 px-1.5 py-0.5 text-xs text-cyan-400">
              VITE_CLERK_PUBLISHABLE_KEY
            </code>{' '}
            to your <code className="rounded bg-slate-800 px-1.5 py-0.5 text-xs text-slate-300">.env</code> file.
          </p>
          <Link to="/" className="text-sm text-cyan-400 hover:underline">
            ← Back to home
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-slate-950 px-4">
      <div className="mb-8 flex items-center gap-2">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-cyan-400/10 ring-1 ring-cyan-400/30">
          <Shield className="h-4 w-4 text-cyan-400" />
        </div>
        <span className="font-bold text-white text-lg">CloudGuard</span>
      </div>

      <SignUp routing="path" path="/sign-up" afterSignUpUrl="/dashboard" />

      <p className="mt-6 text-sm text-slate-500">
        Already have an account?{' '}
        <Link to="/sign-in" className="text-cyan-400 hover:underline">
          Sign in
        </Link>
      </p>
    </div>
  )
}
