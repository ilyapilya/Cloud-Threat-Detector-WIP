import { Link } from 'react-router-dom'
import { Shield, Menu, X } from 'lucide-react'
import { useState } from 'react'
import { Button } from './ui/button'

const clerkConfigured = !!import.meta.env.VITE_CLERK_PUBLISHABLE_KEY

export default function Navbar() {
  const [mobileOpen, setMobileOpen] = useState(false)

  return (
    <nav className="fixed top-0 z-50 w-full border-b border-slate-800/50 bg-slate-950/80 backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-cyan-400/10 ring-1 ring-cyan-400/30">
            <Shield className="h-4 w-4 text-cyan-400" />
          </div>
          <span className="font-bold text-white text-lg tracking-tight">CloudGuard</span>
        </Link>

        {/* Desktop nav */}
        <div className="hidden items-center gap-8 md:flex">
          <a href="#how-it-works" className="text-sm text-slate-400 hover:text-white transition-colors">
            How it works
          </a>
          <a href="#pricing" className="text-sm text-slate-400 hover:text-white transition-colors">
            Pricing
          </a>
        </div>

        {/* Desktop CTA */}
        <div className="hidden items-center gap-3 md:flex">
          {clerkConfigured ? (
            <>
              <Button variant="ghost" size="sm" asChild>
                <Link to="/sign-in">Sign in</Link>
              </Button>
              <Button size="sm" asChild>
                <Link to="/sign-up">Get Started Free</Link>
              </Button>
            </>
          ) : (
            <Button size="sm" asChild>
              <a href="#waitlist">Get Early Access</a>
            </Button>
          )}
        </div>

        {/* Mobile menu toggle */}
        <button
          className="flex items-center justify-center rounded-lg p-2 text-slate-400 hover:bg-slate-800 hover:text-white transition-colors md:hidden"
          onClick={() => setMobileOpen(!mobileOpen)}
          aria-label="Toggle menu"
        >
          {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="border-t border-slate-800 bg-slate-950 px-4 py-4 md:hidden">
          <div className="flex flex-col gap-4">
            <a
              href="#how-it-works"
              className="text-sm text-slate-400 hover:text-white transition-colors"
              onClick={() => setMobileOpen(false)}
            >
              How it works
            </a>
            <a
              href="#pricing"
              className="text-sm text-slate-400 hover:text-white transition-colors"
              onClick={() => setMobileOpen(false)}
            >
              Pricing
            </a>
            <div className="flex flex-col gap-2 pt-2 border-t border-slate-800">
              {clerkConfigured ? (
                <>
                  <Button variant="outline" size="sm" asChild>
                    <Link to="/sign-in" onClick={() => setMobileOpen(false)}>Sign in</Link>
                  </Button>
                  <Button size="sm" asChild>
                    <Link to="/sign-up" onClick={() => setMobileOpen(false)}>Get Started Free</Link>
                  </Button>
                </>
              ) : (
                <Button size="sm" asChild>
                  <a href="#waitlist" onClick={() => setMobileOpen(false)}>Get Early Access</a>
                </Button>
              )}
            </div>
          </div>
        </div>
      )}
    </nav>
  )
}
