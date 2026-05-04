import { useParams, useNavigate } from 'react-router-dom'
import { useEffect } from 'react'
import { useContract } from '../store/ContractContext'
import { useClauses } from '../hooks/useClauses'
import { getOrCreateSession } from '../api/endpoints'
import toast from 'react-hot-toast'
import { motion } from 'framer-motion'
import RiskGauge from '../components/dashboard/RiskGauge'
import RiskDistributionChart from '../components/dashboard/RiskDistributionChart'
import ContractSummaryBar from '../components/dashboard/ContractSummaryBar'
import CriticalClausesSummary from '../components/dashboard/CriticalClausesSummary'
import ClauseList from '../components/dashboard/ClauseList'
import ChatPanel from '../components/chat/ChatPanel'
import Spinner from '../components/shared/Spinner'
import ErrorBanner from '../components/shared/ErrorBanner'

export default function AnalysisPage() {
  const { contractId } = useParams()
  const navigate = useNavigate()
  const { contract, sessionId, clauses, isFetchingClauses, clauseError, filteredClauses, dispatch } = useContract()
  const { fetch: fetchClauses } = useClauses()

  useEffect(() => {
    if (!contract || contract.contract_id !== contractId) {
      navigate('/')
      return
    }

    let sessionInitAttempts = 0
    const maxRetries = 3

    const initializeSession = async () => {
      try {
        console.log(`Initializing session for contract ${contractId}...`)
        const session = await getOrCreateSession(contractId)
        console.log(`✓ Session created: ${session.session_id}`)
        dispatch({ type: 'SET_SESSION', payload: session.session_id })
      } catch (error) {
        console.error('Session init error:', error)
        sessionInitAttempts++
        if (sessionInitAttempts < maxRetries) {
          toast.error('Failed to initialize chat session. Retrying...')
          setTimeout(initializeSession, 2000)
        } else {
          toast.error('Failed to initialize chat session.')
        }
      }
    }

    let clausesInitAttempts = 0
    const loadClauses = async () => {
      try {
        console.log(`Loading clauses for contract ${contractId}...`)
        await fetchClauses()
        console.log(`✓ Clauses loaded`)
      } catch (error) {
        console.error('Clauses load error:', error)
        clausesInitAttempts++
        if (clausesInitAttempts < maxRetries) {
          toast.error('Failed to load clauses. Retrying...')
          setTimeout(loadClauses, 2000)
        } else {
          toast.error('Failed to load clauses.')
        }
      }
    }

    const shouldInitSession = !sessionId
    const shouldLoadClauses = !isFetchingClauses && (!clauses || clauses.length === 0)

    if (shouldInitSession) {
      initializeSession()
    }

    if (shouldLoadClauses) {
      loadClauses()
    }
  }, [contract, contractId, sessionId, clauses, isFetchingClauses, navigate, dispatch, fetchClauses])

  if (!contract) {
    return <Spinner />
  }

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.4 },
    },
  }

  return (
    <motion.div
      className="max-w-7xl mx-auto px-6 py-12 space-y-8"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {clauseError && <ErrorBanner message={clauseError} />}

      {/* Summary Cards */}
      <motion.div className="grid lg:grid-cols-3 gap-6" variants={itemVariants}>
        <RiskGauge score={contract.overall_risk_score} />
        <RiskDistributionChart distribution={contract.risk_distribution} />
        <ContractSummaryBar contract={contract} />
      </motion.div>

      {/* Critical Clauses */}
      {contract.critical_clauses && contract.critical_clauses.length > 0 && (
        <motion.div variants={itemVariants}>
          <CriticalClausesSummary clauses={contract.critical_clauses} />
        </motion.div>
      )}

      {/* Main Content */}
      <motion.div className="grid lg:grid-cols-3 gap-6" variants={itemVariants}>
        {/* Clauses Panel */}
        <div className="lg:col-span-2">
          {isFetchingClauses ? (
            <Spinner />
          ) : (
            <ClauseList clauses={filteredClauses} />
          )}
        </div>

        {/* Chat Panel */}
        <div className="h-[520px] max-h-[70vh] lg:sticky lg:top-24">
          <ChatPanel contractId={contract.contract_id} sessionId={sessionId} />
        </div>
      </motion.div>
    </motion.div>
  )
}
