import { benchmarkLabels, benchmarkColors } from '../../utils/riskUtils'

export default function BenchmarkPill({ position }) {
  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-500 ${benchmarkColors[position]} bg-surface-high border border-border`}>
      {benchmarkLabels[position]}
    </span>
  )
}
