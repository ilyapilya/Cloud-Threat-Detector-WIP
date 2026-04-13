import * as React from 'react'
import { cva } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const badgeVariants = cva(
  'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors',
  {
    variants: {
      variant: {
        default:   'bg-cyan-400/10 text-cyan-400 border border-cyan-400/20',
        critical:  'bg-red-500/10 text-red-400 border border-red-500/20',
        high:      'bg-orange-500/10 text-orange-400 border border-orange-500/20',
        medium:    'bg-yellow-500/10 text-yellow-400 border border-yellow-500/20',
        low:       'bg-blue-500/10 text-blue-400 border border-blue-500/20',
        success:   'bg-green-500/10 text-green-400 border border-green-500/20',
        secondary: 'bg-slate-700 text-slate-300 border border-slate-600',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
)

function Badge({ className, variant, ...props }) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />
}

export { Badge, badgeVariants }
