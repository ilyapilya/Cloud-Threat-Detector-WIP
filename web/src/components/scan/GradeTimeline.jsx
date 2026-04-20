/**
 * GradeTimeline — pure SVG sparkline of grade history.
 * Maps A→5, B→4, C→3, D→2, F→1 so higher is better (top of chart).
 */

const GRADE_VALUE = { A: 5, B: 4, C: 3, D: 2, F: 1 }
const GRADE_COLOR = {
  A: '#4ade80',
  B: '#22d3ee',
  C: '#facc15',
  D: '#fb923c',
  F: '#f87171',
}

const W = 280
const H = 56
const PAD_X = 8
const PAD_Y = 8

export default function GradeTimeline({ scans }) {
  // Only use completed scans with a grade, most recent last (chart reads left→right)
  const points = scans
    .filter(s => s.status === 'completed' && s.grade)
    .slice(-8)
    .reverse()

  if (points.length < 2) return null

  const xs = points.map((_, i) =>
    PAD_X + (i / (points.length - 1)) * (W - PAD_X * 2)
  )
  const ys = points.map(p => {
    const val = GRADE_VALUE[p.grade] ?? 3
    // val 1–5 → y from bottom (H-PAD_Y) to top (PAD_Y)
    return H - PAD_Y - ((val - 1) / 4) * (H - PAD_Y * 2)
  })

  const polyline = xs.map((x, i) => `${x},${ys[i]}`).join(' ')
  const lastGrade = points[points.length - 1].grade
  const lineColor = GRADE_COLOR[lastGrade] ?? '#94a3b8'

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/50 px-5 py-4">
      <p className="mb-3 text-xs font-semibold uppercase tracking-widest text-slate-500">
        Grade trend — last {points.length} scans
      </p>
      <svg viewBox={`0 0 ${W} ${H}`} width="100%" height={H} aria-hidden="true">
        {/* Horizontal grid lines for each grade */}
        {[1, 2, 3, 4, 5].map(val => {
          const y = H - PAD_Y - ((val - 1) / 4) * (H - PAD_Y * 2)
          const label = Object.entries(GRADE_VALUE).find(([, v]) => v === val)?.[0]
          return (
            <g key={val}>
              <line
                x1={PAD_X} y1={y} x2={W - PAD_X} y2={y}
                stroke="#1e293b" strokeWidth="1"
              />
              <text x={0} y={y + 4} fill="#475569" fontSize="9" fontWeight="600">
                {label}
              </text>
            </g>
          )
        })}

        {/* Trend line */}
        <polyline
          points={polyline}
          fill="none"
          stroke={lineColor}
          strokeWidth="2"
          strokeLinejoin="round"
          strokeLinecap="round"
          opacity="0.8"
        />

        {/* Data points */}
        {xs.map((x, i) => (
          <circle
            key={i}
            cx={x} cy={ys[i]} r="3.5"
            fill={GRADE_COLOR[points[i].grade] ?? '#94a3b8'}
            stroke="#0f172a" strokeWidth="1.5"
          />
        ))}
      </svg>
    </div>
  )
}
