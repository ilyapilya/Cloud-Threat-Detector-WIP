import { EyeOff, TrendingUp, Clock } from 'lucide-react'
import { Card, CardContent } from '../ui/card'

const problems = [
  {
    icon: EyeOff,
    stat: '80%',
    title: 'Of breaches start with misconfiguration',
    description:
      'S3 buckets, security groups, IAM policies — a single misconfigured resource can expose your entire environment. Most teams don\'t find out until it\'s too late.',
    color: 'text-red-400',
    bgColor: 'bg-red-500/5',
    borderColor: 'border-red-500/10',
  },
  {
    icon: Clock,
    stat: '277',
    title: 'Days average time to detect a breach',
    description:
      'Your cloud is changing constantly. A developer spins up a new EC2 instance or relaxes a security group "temporarily" — and that becomes permanent. Manual reviews can\'t keep pace.',
    color: 'text-orange-400',
    bgColor: 'bg-orange-500/5',
    borderColor: 'border-orange-500/10',
  },
  {
    icon: TrendingUp,
    stat: '$50K',
    title: 'Cost of a manual security audit',
    description:
      'External penetration tests and audits are expensive, infrequent, and produce a report you have to act on manually. You need continuous, automated coverage — not a quarterly snapshot.',
    color: 'text-yellow-400',
    bgColor: 'bg-yellow-500/5',
    borderColor: 'border-yellow-500/10',
  },
]

export default function Problem() {
  return (
    <section className="py-24 px-4">
      <div className="mx-auto max-w-7xl">
        <div className="mb-16 text-center">
          <p className="mb-3 text-sm font-semibold uppercase tracking-widest text-cyan-400">
            The Problem
          </p>
          <h2 className="text-3xl font-bold text-white sm:text-4xl">
            Your cloud is public by default.
            <br />
            <span className="text-slate-400">Most teams don't know it.</span>
          </h2>
        </div>

        <div className="grid gap-6 md:grid-cols-3">
          {problems.map(({ icon: Icon, stat, title, description, color, bgColor, borderColor }) => (
            <Card key={title} className={`border ${borderColor} ${bgColor} p-6`}>
              <CardContent className="p-0 space-y-4">
                <div className={`inline-flex h-12 w-12 items-center justify-center rounded-xl border ${borderColor} ${bgColor}`}>
                  <Icon className={`h-6 w-6 ${color}`} />
                </div>
                <div>
                  <p className={`text-4xl font-extrabold ${color} mb-1`}>{stat}</p>
                  <p className="font-semibold text-white">{title}</p>
                </div>
                <p className="text-sm text-slate-400 leading-relaxed">{description}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}
