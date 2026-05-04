import { getRiskGaugeColor } from '../../utils/riskUtils'
import { motion } from 'framer-motion'

export default function RiskGauge({ score }) {
  const color = getRiskGaugeColor(score)
  const colorMap = {
    critical: '#EF4444',
    high: '#F97316',
    medium: '#EAB308',
    low: '#22C55E',
  }
  const colorBg = {
    critical: 'from-red-900/30 to-red-900/10',
    high: 'from-orange-900/30 to-orange-900/10',
    medium: 'from-yellow-900/30 to-yellow-900/10',
    low: 'from-green-900/30 to-green-900/10',
  }

  const circumference = 2 * Math.PI * 45
  const strokeDashoffset = circumference - (score / 100) * circumference

  return (
    <motion.div
      className={`card p-8 bg-gradient-to-br ${colorBg[color]}`}
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
    >
      <h3 className="font-semibold text-text mb-6">Overall Risk Score</h3>
      <div className="flex flex-col items-center justify-center">
        <div className="relative w-40 h-40">
          <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
            <circle
              cx="50"
              cy="50"
              r="45"
              fill="none"
              stroke="#1E1E2E"
              strokeWidth="8"
            />
            <motion.circle
              cx="50"
              cy="50"
              r="45"
              fill="none"
              stroke={colorMap[color]}
              strokeWidth="8"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              initial={{ strokeDashoffset: circumference }}
              animate={{ strokeDashoffset }}
              transition={{ duration: 1, ease: "easeOut" }}
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <motion.div
              className="text-center"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
            >
              <div className="text-4xl font-bold text-text">{score}</div>
              <div className="text-xs text-muted">out of 100</div>
            </motion.div>
          </div>
        </div>
        <div className="mt-6 text-center">
          <div className={`text-sm font-semibold ${{
            critical: 'text-critical',
            high: 'text-high',
            medium: 'text-medium',
            low: 'text-low',
          }[color]}`}>
            {color.toUpperCase()} RISK
          </div>
        </div>
      </div>
    </motion.div>
  )
}
