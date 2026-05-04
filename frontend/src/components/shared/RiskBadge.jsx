import { riskColors, riskTextColors, riskBgColors } from '../../utils/riskUtils'
import { AlertTriangle } from 'lucide-react'

export default function RiskBadge({ level, size = 'md' }) {
  const sizeClass = size === 'sm' ? 'text-xs px-2 py-1' : 'text-sm px-3 py-1.5'
  const bgClass = riskBgColors[level]
  const textClass = riskTextColors[level]

  return (
    <span className={`risk-badge ${bgClass} ${sizeClass} ${textClass} inline-flex items-center gap-1`}>
      {level === 'CRITICAL' && <AlertTriangle className="w-3 h-3" />}
      {level}
    </span>
  )
}
