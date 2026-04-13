import { Routes, Route } from 'react-router-dom'
import Landing from './pages/Landing'
import SignInPage from './pages/SignIn'
import SignUpPage from './pages/SignUp'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/sign-in/*" element={<SignInPage />} />
      <Route path="/sign-up/*" element={<SignUpPage />} />
    </Routes>
  )
}
