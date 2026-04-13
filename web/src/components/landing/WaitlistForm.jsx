import { useState } from 'react'
import { ArrowRight, Loader2, CheckCircle2 } from 'lucide-react'
import { Button } from '../ui/button'
import { Input } from '../ui/input'
import { supabase } from '@/lib/supabase'

export default function WaitlistForm({ className = '' }) {
  const [email, setEmail] = useState('')
  const [status, setStatus] = useState('idle') // idle | loading | success | error
  const [errorMsg, setErrorMsg] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    if (!email) return

    setStatus('loading')
    setErrorMsg('')

    try {
      const { error } = await supabase
        .from('waitlist')
        .insert({ email: email.toLowerCase().trim() })

      if (error) {
        if (error.code === '23505') {
          // Duplicate — treat as success, don't reveal
          setStatus('success')
        } else {
          throw error
        }
      } else {
        setStatus('success')
      }
    } catch (err) {
      console.error('Waitlist insert error:', err)
      setErrorMsg('Something went wrong. Please try again.')
      setStatus('error')
    }
  }

  if (status === 'success') {
    return (
      <div className={`flex flex-col items-center gap-3 rounded-xl border border-green-500/20 bg-green-500/5 px-6 py-5 ${className}`}>
        <CheckCircle2 className="h-8 w-8 text-green-400" />
        <p className="font-semibold text-white">You're on the list!</p>
        <p className="text-sm text-slate-400 text-center">
          We'll email you as soon as CloudGuard is ready for early access.
        </p>
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit} className={`flex flex-col gap-3 ${className}`}>
      <div className="flex gap-2">
        <Input
          type="email"
          placeholder="you@company.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          disabled={status === 'loading'}
          className="h-12 text-base"
        />
        <Button
          type="submit"
          size="lg"
          disabled={status === 'loading' || !email}
          className="shrink-0"
        >
          {status === 'loading' ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <>
              Get Early Access
              <ArrowRight className="h-4 w-4" />
            </>
          )}
        </Button>
      </div>

      {status === 'error' && (
        <p className="text-sm text-red-400">{errorMsg}</p>
      )}

      <p className="text-xs text-slate-500 text-center">
        Free forever for the first 5 findings per scan. No credit card required.
      </p>
    </form>
  )
}
