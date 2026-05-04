import { useContract } from '../store/ContractContext'
import { analyzeContract, getClauses } from '../api/endpoints'

export const useAnalyze = () => {
  const { dispatch } = useContract()

  const analyze = async (file) => {
    dispatch({ type: 'ANALYZE_START' })
    try {
      const response = await analyzeContract(file)
      dispatch({ type: 'ANALYZE_SUCCESS', payload: response })
      return response
    } catch (error) {
      dispatch({ type: 'ANALYZE_ERROR', payload: error.message })
      throw error
    }
  }

  return { analyze }
}
