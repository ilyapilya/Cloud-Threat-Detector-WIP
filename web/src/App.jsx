import { Routes, Route } from 'react-router-dom'
import ProtectedRoute from './components/ProtectedRoute'
import Landing    from './pages/Landing'
import SignInPage from './pages/SignIn'
import SignUpPage from './pages/SignUp'
import Dashboard  from './pages/Dashboard'
import NewScan    from './pages/NewScan'
import ScanResults from './pages/ScanResults'
import History    from './pages/History'

export default function App() {
  return (
    <Routes>
      {/* Public */}
      <Route path="/"          element={<Landing />} />
      <Route path="/sign-in/*" element={<SignInPage />} />
      <Route path="/sign-up/*" element={<SignUpPage />} />

      {/* Protected */}
      <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
      <Route path="/scan/new"  element={<ProtectedRoute><NewScan /></ProtectedRoute>} />
      <Route path="/scan/:id"  element={<ProtectedRoute><ScanResults /></ProtectedRoute>} />
      <Route path="/history"   element={<ProtectedRoute><History /></ProtectedRoute>} />
    </Routes>
  )
}