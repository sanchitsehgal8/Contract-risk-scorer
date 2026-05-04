import { useMemo, useState } from 'react'
import { ChevronDown, AlertTriangle } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import RiskBadge from '../shared/RiskBadge'
import BenchmarkPill from '../shared/BenchmarkPill'

export default function ClauseCard({ clause }) {
  const [isExpanded, setIsExpanded] = useState(false)
  const [isClauseTextExpanded, setIsClauseTextExpanded] = useState(false)
  const [isRiskExpanded, setIsRiskExpanded] = useState(false)

  const isClauseTextLong = useMemo(
    () => clause?.clause_text && clause.clause_text.length > 320,
    [clause?.clause_text]
  )
  const isRiskLong = useMemo(
    () => clause?.risk_reason && clause.risk_reason.length > 220,
    [clause?.risk_reason]
  )

  return (
    <motion.div
      className="card overflow-hidden hover:border-violet/30 cursor-pointer transition-all"
      onClick={() => setIsExpanded(!isExpanded)}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
    >
      {/* Header */}
      <div className="p-4 flex items-start justify-between gap-4 bg-surface-high/30">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2">
            <h3 className="font-semibold text-text">{clause.clause_type}</h3>
            <RiskBadge level={clause.risk_level} size="sm" />
          </div>
          <p className="text-xs text-muted">
            Page {clause.page_num} • Confidence {Math.round(clause.confidence_score * 100)}%
          </p>
        </div>
        <motion.div
          animate={{ rotate: isExpanded ? 180 : 0 }}
          transition={{ duration: 0.2 }}
        >
          <ChevronDown className="w-5 h-5 text-muted" />
        </motion.div>
      </div>

      {/* Content */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            className="p-4 space-y-4 border-t border-border"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            {/* Clause Text */}
            <div>
              <p className="text-xs font-500 text-muted mb-2">Clause Text</p>
              <p
                className={`code-text bg-bg p-3 rounded-lg text-xs text-muted leading-relaxed ${
                  isClauseTextLong && !isClauseTextExpanded ? 'max-h-24 overflow-hidden' : ''
                }`}
              >
                {clause.clause_text}
              </p>
              {isClauseTextLong && (
                <button
                  type="button"
                  onClick={(event) => {
                    event.stopPropagation()
                    setIsClauseTextExpanded(!isClauseTextExpanded)
                  }}
                  className="mt-2 text-xs text-blue hover:underline"
                >
                  {isClauseTextExpanded ? 'Show less' : 'Show more'}
                </button>
              )}
            </div>

            {/* Risk Analysis */}
            <div>
              <p className="text-xs font-500 text-muted mb-2">Risk Analysis</p>
              <p
                className={`text-sm text-text ${
                  isRiskLong && !isRiskExpanded ? 'max-h-16 overflow-hidden' : ''
                }`}
              >
                {clause.risk_reason}
              </p>
              {isRiskLong && (
                <button
                  type="button"
                  onClick={(event) => {
                    event.stopPropagation()
                    setIsRiskExpanded(!isRiskExpanded)
                  }}
                  className="mt-2 text-xs text-blue hover:underline"
                >
                  {isRiskExpanded ? 'Show less' : 'Show more'}
                </button>
              )}
            </div>

            {/* Benchmark & Dispute */}
            <div className="flex flex-wrap items-center gap-3">
              <BenchmarkPill position={clause.benchmark_position} />
              {clause.dispute_prone && (
                <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-500 bg-red-950/30 border border-red-800 text-critical">
                  <AlertTriangle className="w-3 h-3" />
                  Dispute History
                </span>
              )}
            </div>

            {/* Suggestion */}
            <div>
              <p className="text-xs font-500 text-muted mb-2">Suggested Revision</p>
              <p className="text-sm text-text bg-violet/5 border border-violet/20 p-3 rounded-lg">
                {clause.suggested_revision}
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}
