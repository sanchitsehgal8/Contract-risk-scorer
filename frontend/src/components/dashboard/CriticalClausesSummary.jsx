import RiskBadge from '../shared/RiskBadge'
import { AlertTriangle } from 'lucide-react'

export default function CriticalClausesSummary({ clauses }) {
  return (
    <div className="card p-6">
      <div className="flex items-center gap-2 mb-4">
        <AlertTriangle className="w-5 h-5 text-critical" />
        <h3 className="font-semibold text-text">Critical Issues ({clauses.length})</h3>
      </div>
      
      <div className="space-y-3">
        {clauses.slice(0, 3).map((clause, i) => (
          <div key={i} className="p-3 bg-surface-high rounded-lg border border-red-800/30">
            <div className="flex items-start justify-between gap-2 mb-2">
              <h4 className="font-500 text-text">{clause.clause_type}</h4>
              <RiskBadge level={clause.risk_level} size="sm" />
            </div>
            <p className="text-xs text-muted line-clamp-2">{clause.brief_reason}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
