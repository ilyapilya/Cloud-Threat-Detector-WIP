import { Check, Zap } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Button } from '../ui/button'
import { Badge } from '../ui/badge'
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '../ui/card'

const clerkConfigured = !!import.meta.env.VITE_CLERK_PUBLISHABLE_KEY

const plans = [
  {
    name: 'Starter',
    price: '$0',
    period: 'forever',
    description: 'For developers exploring cloud security.',
    badge: null,
    features: [
      'Up to 5 findings per scan',
      'Basic severity classification',
      '1 scan per day',
      'AWS support',
      'Community support',
    ],
    cta: 'Get Started Free',
    ctaVariant: 'outline',
    ctaHref: clerkConfigured ? '/sign-up' : '#waitlist',
    highlight: false,
  },
  {
    name: 'Pro',
    price: '$29',
    period: '/month',
    description: 'For teams serious about cloud security posture.',
    badge: 'Most Popular',
    features: [
      'Unlimited findings per scan',
      'AI remediation for every finding',
      'Unlimited scans',
      'Full scan history',
      'Shareable scan report card',
      'AWS + Azure + GCP',
      'Priority support',
    ],
    cta: 'Start Pro Trial',
    ctaVariant: 'default',
    ctaHref: clerkConfigured ? '/sign-up' : '#waitlist',
    highlight: true,
  },
]

export default function PricingTeaser() {
  return (
    <section id="pricing" className="py-24 px-4">
      <div className="mx-auto max-w-7xl">
        <div className="mb-16 text-center">
          <p className="mb-3 text-sm font-semibold uppercase tracking-widest text-cyan-400">
            Pricing
          </p>
          <h2 className="text-3xl font-bold text-white sm:text-4xl">
            Start free. Upgrade when you're ready.
          </h2>
          <p className="mt-4 text-slate-400">
            No credit card required for the free tier.
          </p>
        </div>

        <div className="mx-auto grid max-w-4xl gap-6 md:grid-cols-2">
          {plans.map((plan) => (
            <Card
              key={plan.name}
              className={`relative flex flex-col ${
                plan.highlight
                  ? 'border-cyan-500/30 bg-slate-900/80 ring-1 ring-cyan-500/20'
                  : 'border-slate-800'
              }`}
            >
              {plan.badge && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <Badge className="px-3 py-1 text-xs font-semibold">
                    <Zap className="mr-1 h-3 w-3" />
                    {plan.badge}
                  </Badge>
                </div>
              )}

              <CardHeader className="pb-4">
                <CardTitle className="text-xl">{plan.name}</CardTitle>
                <CardDescription>{plan.description}</CardDescription>
                <div className="flex items-baseline gap-1 pt-2">
                  <span className="text-4xl font-extrabold text-white">{plan.price}</span>
                  <span className="text-slate-400">{plan.period}</span>
                </div>
              </CardHeader>

              <CardContent className="flex-1">
                <ul className="space-y-3">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-center gap-3 text-sm text-slate-300">
                      <Check className="h-4 w-4 shrink-0 text-cyan-400" />
                      {feature}
                    </li>
                  ))}
                </ul>
              </CardContent>

              <CardFooter className="pt-6">
                <Button
                  variant={plan.ctaVariant}
                  size="lg"
                  className="w-full"
                  asChild
                >
                  {clerkConfigured ? (
                    <Link to={plan.ctaHref}>{plan.cta}</Link>
                  ) : (
                    <a href={plan.ctaHref}>{plan.cta}</a>
                  )}
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>

        <p className="mt-8 text-center text-sm text-slate-500">
          Prices in USD. Cancel anytime. Questions?{' '}
          <a href="mailto:hello@cloudguard.dev" className="text-cyan-400 hover:underline">
            Contact us
          </a>
        </p>
      </div>
    </section>
  )
}
