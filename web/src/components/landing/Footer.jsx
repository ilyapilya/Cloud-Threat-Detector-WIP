import { Shield, Github } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function Footer() {
  return (
    <footer className="border-t border-slate-800 bg-slate-950 px-4 py-12">
      <div className="mx-auto max-w-7xl">
        <div className="flex flex-col items-center justify-between gap-8 md:flex-row">
          {/* Brand */}
          <div className="flex flex-col items-center gap-3 md:items-start">
            <Link to="/" className="flex items-center gap-2">
              <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-cyan-400/10 ring-1 ring-cyan-400/30">
                <Shield className="h-3.5 w-3.5 text-cyan-400" />
              </div>
              <span className="font-bold text-white">CloudGuard</span>
            </Link>
            <p className="text-sm text-slate-500 text-center md:text-left">
              Detect cloud vulnerabilities before attackers do.
            </p>
          </div>

          {/* Links */}
          <nav className="flex flex-wrap justify-center gap-x-8 gap-y-3">
            <a href="#how-it-works" className="text-sm text-slate-500 hover:text-white transition-colors">
              How it works
            </a>
            <a href="#pricing" className="text-sm text-slate-500 hover:text-white transition-colors">
              Pricing
            </a>
            <a href="#" className="text-sm text-slate-500 hover:text-white transition-colors">
              Privacy Policy
            </a>
            <a href="#" className="text-sm text-slate-500 hover:text-white transition-colors">
              Terms of Service
            </a>
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1.5 text-sm text-slate-500 hover:text-white transition-colors"
            >
              <Github className="h-4 w-4" />
              GitHub
            </a>
          </nav>
        </div>

        <div className="mt-8 border-t border-slate-800 pt-8 text-center">
          <p className="text-xs text-slate-600">
            &copy; {new Date().getFullYear()} CloudGuard. Built for cloud engineers who ship fast.
          </p>
        </div>
      </div>
    </footer>
  )
}
