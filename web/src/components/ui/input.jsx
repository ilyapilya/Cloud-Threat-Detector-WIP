import * as React from 'react'
import { cn } from '@/lib/utils'

const Input = React.forwardRef(({ className, type, ...props }, ref) => {
  return (
    <input
      type={type}
      className={cn(
        'flex h-10 w-full rounded-lg border border-slate-700 bg-slate-800/50 px-4 py-2',
        'text-sm text-slate-100 placeholder:text-slate-500',
        'transition-colors focus:border-cyan-500 focus:outline-none focus:ring-1 focus:ring-cyan-500/40',
        'disabled:cursor-not-allowed disabled:opacity-50',
        className
      )}
      ref={ref}
      {...props}
    />
  )
})
Input.displayName = 'Input'

export { Input }
