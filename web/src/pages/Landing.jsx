import { Helmet } from 'react-helmet-async'
import Navbar from '../components/Navbar'
import Hero from '../components/landing/Hero'
import Problem from '../components/landing/Problem'
import HowItWorks from '../components/landing/HowItWorks'
import PricingTeaser from '../components/landing/PricingTeaser'
import Footer from '../components/landing/Footer'

export default function Landing() {
  return (
    <>
      <Helmet>
        <title>CloudGuard — Cloud Security Scanner</title>
        <meta
          name="description"
          content="Detect AWS misconfigurations before attackers exploit them. AI-powered remediation included. Free tier available."
        />
      </Helmet>

      <div className="min-h-screen bg-slate-950">
        <Navbar />
        <main>
          <Hero />
          <Problem />
          <HowItWorks />
          <PricingTeaser />
        </main>
        <Footer />
      </div>
    </>
  )
}
