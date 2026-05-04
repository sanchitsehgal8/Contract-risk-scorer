import { useCallback } from 'react'
import { useContract } from '../store/ContractContext'
import { getClauses } from '../api/endpoints'

export const useClauses = () => {
  const { contract, dispatch } = useContract()

  const fetch = useCallback(async () => {
    if (!contract?.contract_id) return
    dispatch({ type: 'CLAUSES_START' })
    try {
      const response = await getClauses(contract.contract_id)
      dispatch({ type: 'CLAUSES_SUCCESS', payload: response })
      return response
    } catch (error) {
      dispatch({ type: 'CLAUSES_ERROR', payload: error.message })
      throw error
    }
  }, [contract?.contract_id, dispatch])

  return { fetch }
}
