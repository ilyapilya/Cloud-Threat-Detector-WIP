import { useAuth } from '@clerk/clerk-react'
import { Navigate, useLocation } from 'react-router-dom'
import { Shield } from 'lucide-react'

export default function ProtectedRoute({ children }) {
  const { isLoaded, isSignedIn } = useAuth()
  const location = useLocation()

  // Show a minimal skeleton while Clerk loads — prevents redirect flash
  if (!isLoaded) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950">
        <div className="flex flex-col items-center gap-3">
          <Shield className="h-8 w-8 animate-pulse text-cyan-400" />
          <p className="text-sm text-slate-500">Loading...</p>
        </div>
      </div>
    )
  }

  if (!isSignedIn) {
    // Preserve the intended destination so Clerk can redirect back after sign-in
    return <Navigate to={`/sign-in?redirect_url=${encodeURIComponent(location.pathname)}`} replace />
  }

  return children
}