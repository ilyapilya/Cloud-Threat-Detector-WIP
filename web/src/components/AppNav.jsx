import { Link, useLocation } from 'react-router-dom'
import { Shield, LayoutDashboard, History, Plus } from 'lucide-react'
import { UserButton } from '@clerk/clerk-react'
import { Button } from './ui/button'
import { cn } from '@/lib/utils'

const navLinks = [
  { label: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { label: 'History',   href: '/history',   icon: History, soon: true },
]

export default function AppNav() {
  const { pathname } = useLocation()

  return (
    <nav className="fixed top-0 z-50 w-full border-b border-slate-800/50 bg-slate-950/90 backdrop-blur-xl">
      <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4 sm:px-6">
        {/* Logo */}
        <Link to="/dashboard" className="flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-cyan-400/10 ring-1 ring-cyan-400/30">
            <Shield className="h-3.5 w-3.5 text-cyan-400" />
          </div>
          <span className="font-bold text-white tracking-tight">CloudGuard</span>
        </Link>

        {/* Nav links */}
        <div className="hidden items-center gap-1 md:flex">
          {navLinks.map(({ label, href, icon: Icon, soon }) => (
            <Link
              key={href}
              to={soon ? '#' : href}
              className={cn(
                'flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm transition-colors',
                soon
                  ? 'cursor-default text-slate-600'
                  : pathname === href
                    ? 'bg-slate-800 text-white'
                    : 'text-slate-400 hover:bg-slate-800/60 hover:text-white'
              )}
            >
              <Icon className="h-3.5 w-3.5" />
              {label}
              {soon && (
                <span className="rounded-full bg-slate-800 px-1.5 py-0.5 text-[10px] text-slate-500">
                  soon
                </span>
              )}
            </Link>
          ))}
        </div>

        {/* Actions */}
        <div className="flex items-center gap-3">
          <Button size="sm" asChild>
            <Link to="/scan/new">
              <Plus className="h-3.5 w-3.5" />
              New Scan
            </Link>
          </Button>
          <UserButton afterSignOutUrl="/" />
        </div>
      </div>
    </nav>
  )
}