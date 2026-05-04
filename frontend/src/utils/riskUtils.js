export const riskLevelOrder = { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3 }

export const riskColors = {
  CRITICAL: '#EF4444',
  HIGH: '#F97316',
  MEDIUM: '#EAB308',
  LOW: '#22C55E',
}

export const riskBgColors = {
  CRITICAL: 'bg-red-950/30 border-red-800',
  HIGH: 'bg-orange-950/30 border-orange-800',
  MEDIUM: 'bg-yellow-950/30 border-yellow-800',
  LOW: 'bg-green-950/30 border-green-800',
}

export const riskTextColors = {
  CRITICAL: 'text-critical',
  HIGH: 'text-high',
  MEDIUM: 'text-medium',
  LOW: 'text-low',
}

export const getRiskGaugeColor = (score) => {
  if (score >= 80) return 'critical'
  if (score >= 60) return 'high'
  if (score >= 40) return 'medium'
  return 'low'
}

export const benchmarkLabels = {
  market_standard: 'Market Standard',
  above_market: 'Above Market',
  below_market: 'Below Market',
}

export const benchmarkColors = {
  market_standard: 'text-blue-400',
  above_market: 'text-orange-400',
  below_market: 'text-green-400',
}

export const filterOptions = [
  { value: 'ALL', label: 'All Clauses' },
  { value: 'CRITICAL', label: 'Critical' },
  { value: 'HIGH', label: 'High' },
  { value: 'MEDIUM', label: 'Medium' },
  { value: 'LOW', label: 'Low' },
  { value: 'DISPUTE', label: 'Dispute History' },
]

export const sortOptions = [
  { value: 'risk_level', label: 'Risk Level' },
  { value: 'clause_type', label: 'Clause Type' },
  { value: 'page_num', label: 'Page Number' },
]
