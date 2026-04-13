import { Link2, ScanSearch, Wand2 } from 'lucide-react'

const steps = [
  {
    number: '01',
    icon: Link2,
    title: 'Connect Your AWS Account',
    description:
      'Paste your IAM access key or deploy our one-click read-only CloudFormation template. We never request write permissions — your resources are always safe.',
    detail: 'Supports IAM credentials and cross-account roles',
  },
  {
    number: '02',
    icon: ScanSearch,
    title: 'We Scan 20+ Security Controls',
    description:
      'Our engine checks S3 public access, open security groups, unencrypted volumes, disabled MFA, missing CloudTrail logs, over-permissive IAM policies, and more.',
    detail: 'Full scan completes in under 60 seconds',
  },
  {
    number: '03',
    icon: Wand2,
    title: 'Get AI-Powered Fix Instructions',
    description:
      'Claude AI analyzes each finding and generates specific CLI commands, console walk-throughs, and risk assessments — tailored to your exact configuration.',
    detail: 'Copy-paste CLI commands ready to run',
  },
]

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="py-24 px-4 bg-slate-900/30">
      <div className="mx-auto max-w-7xl">
        <div className="mb-16 text-center">
          <p className="mb-3 text-sm font-semibold uppercase tracking-widest text-cyan-400">
            How It Works
          </p>
          <h2 className="text-3xl font-bold text-white sm:text-4xl">
            Enterprise-grade security in{' '}
            <span className="text-gradient">3 simple steps</span>
          </h2>
        </div>

        <div className="relative">
          {/* Connector line (desktop) */}
          <div className="absolute left-0 right-0 top-12 hidden h-px bg-gradient-to-r from-transparent via-cyan-400/20 to-transparent md:block" />

          <div className="grid gap-8 md:grid-cols-3">
            {steps.map(({ number, icon: Icon, title, description, detail }) => (
              <div key={number} className="relative flex flex-col items-center text-center">
                {/* Number badge */}
                <div className="relative mb-6 flex h-24 w-24 items-center justify-center rounded-2xl border border-slate-700 bg-slate-900 shadow-lg shadow-slate-950/50">
                  <Icon className="h-10 w-10 text-cyan-400" />
                  <span className="absolute -right-2 -top-2 flex h-6 w-6 items-center justify-center rounded-full bg-cyan-400 text-xs font-bold text-slate-950">
                    {number.slice(1)}
                  </span>
                </div>

                <h3 className="mb-3 text-lg font-semibold text-white">{title}</h3>
                <p className="mb-4 text-sm text-slate-400 leading-relaxed">{description}</p>
                <span className="inline-flex items-center rounded-full border border-slate-700 bg-slate-800/50 px-3 py-1 text-xs text-slate-400">
                  {detail}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
