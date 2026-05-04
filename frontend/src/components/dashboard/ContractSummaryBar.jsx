import { useEffect, useMemo, useState } from 'react'
import { AlertTriangle, Download } from 'lucide-react'
import { downloadReport, getContractSummary } from '../../api/endpoints'
import toast from 'react-hot-toast'

export default function ContractSummaryBar({ contract }) {
  const [summary, setSummary] = useState('')
  const [isLoadingSummary, setIsLoadingSummary] = useState(false)
  const [summaryError, setSummaryError] = useState('')
  const [isSummaryExpanded, setIsSummaryExpanded] = useState(false)

  const isSummaryLong = useMemo(() => summary && summary.length > 240, [summary])

  useEffect(() => {
    let isMounted = true
    const fetchSummary = async () => {
      if (!contract?.contract_id) return
      setIsLoadingSummary(true)
      setSummaryError('')
      try {
        const response = await getContractSummary(contract.contract_id)
        if (isMounted) {
          setSummary(response.summary || '')
        }
      } catch (error) {
        if (isMounted) {
          setSummaryError('Failed to load summary')
        }
      } finally {
        if (isMounted) {
          setIsLoadingSummary(false)
        }
      }
    }

    fetchSummary()
    return () => {
      isMounted = false
    }
  }, [contract?.contract_id])

  const handleDownload = async () => {
    try {
      const loading = toast.loading('Downloading report...')
      await downloadReport(contract.contract_id)
      toast.dismiss(loading)
      toast.success('Report downloaded')
    } catch (error) {
      toast.error('Failed to download report')
    }
  }

  return (
    <div className="card p-6 space-y-4">
      <h3 className="font-semibold text-text">Contract Summary</h3>
      
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-sm text-muted">Total Clauses</span>
          <span className="font-semibold text-text">{contract.total_clauses}</span>
        </div>
        <div className="h-px bg-border" />

        <div className="space-y-2">
          <span className="text-sm text-muted">Summary</span>
          {isLoadingSummary ? (
            <p className="text-sm text-text">Generating summary...</p>
          ) : summaryError ? (
            <p className="text-sm text-red-400">{summaryError}</p>
          ) : (
            <div>
              <p className={`text-sm text-text leading-relaxed ${isSummaryLong && !isSummaryExpanded ? 'max-h-16 overflow-hidden' : ''}`}>
                {summary || 'No summary available.'}
              </p>
              {isSummaryLong && (
                <button
                  type="button"
                  onClick={() => setIsSummaryExpanded(!isSummaryExpanded)}
                  className="mt-2 text-xs text-blue hover:underline"
                >
                  {isSummaryExpanded ? 'Show less' : 'Show more'}
                </button>
              )}
            </div>
          )}
        </div>
        <div className="h-px bg-border" />
        
        <div className="flex items-center justify-between">
          <span className="text-sm text-muted flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-critical" />
            Critical Issues
          </span>
          <span className="font-semibold text-critical">{contract.critical_clauses.length}</span>
        </div>
        <div className="h-px bg-border" />

        <button
          onClick={handleDownload}
          className="w-full btn btn-primary mt-2"
        >
          <Download className="w-4 h-4" />
          Download Report
        </button>
      </div>
    </div>
  )
}
