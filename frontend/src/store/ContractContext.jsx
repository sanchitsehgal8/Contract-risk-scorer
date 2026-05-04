import { createContext, useContext, useReducer, useCallback, useState } from 'react'

const ContractContext = createContext()

const initialState = {
  contract: null,
  clauses: [],
  sessionId: null,
  isAnalyzing: false,
  isFetchingClauses: false,
  analyzeError: null,
  clauseError: null,
  activeFilter: 'ALL',
  searchQuery: '',
  sortBy: 'risk_level'
}

const reducer = (state, action) => {
  switch (action.type) {
    case 'ANALYZE_START':
      return { ...state, isAnalyzing: true, analyzeError: null }
    case 'ANALYZE_SUCCESS':
      return {
        ...state,
        isAnalyzing: false,
        contract: action.payload,
        sessionId: action.payload.session_id,
      }
    case 'ANALYZE_ERROR':
      return { ...state, isAnalyzing: false, analyzeError: action.payload }
    case 'CLAUSES_START':
      return { ...state, isFetchingClauses: true, clauseError: null }
    case 'CLAUSES_SUCCESS':
      return { ...state, isFetchingClauses: false, clauses: action.payload }
    case 'CLAUSES_ERROR':
      return { ...state, isFetchingClauses: false, clauseError: action.payload }
    case 'SET_SESSION':
      return { ...state, sessionId: action.payload }
    case 'SET_FILTER':
      return { ...state, activeFilter: action.payload }
    case 'SET_SEARCH':
      return { ...state, searchQuery: action.payload }
    case 'SET_SORT':
      return { ...state, sortBy: action.payload }
    case 'RESET':
      return initialState
    default:
      return state
  }
}

export const ContractProvider = ({ children }) => {
  const [state, dispatch] = useReducer(reducer, initialState)

  const getFilteredClauses = useCallback(() => {
    let filtered = [...state.clauses]

    // Filter by risk level
    if (state.activeFilter !== 'ALL') {
      if (state.activeFilter === 'DISPUTE') {
        filtered = filtered.filter(c => c.dispute_prone)
      } else {
        filtered = filtered.filter(c => c.risk_level === state.activeFilter)
      }
    }

    // Filter by search query
    if (state.searchQuery) {
      const q = state.searchQuery.toLowerCase()
      filtered = filtered.filter(c =>
        c.clause_type.toLowerCase().includes(q) ||
        c.clause_text.toLowerCase().includes(q)
      )
    }

    // Sort
    const sortMap = {
      risk_level: (a, b) => {
        const order = { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3 }
        return order[a.risk_level] - order[b.risk_level]
      },
      clause_type: (a, b) => a.clause_type.localeCompare(b.clause_type),
      page_num: (a, b) => a.page_num - b.page_num,
    }

    if (sortMap[state.sortBy]) {
      filtered.sort(sortMap[state.sortBy])
    }

    return filtered
  }, [state.clauses, state.activeFilter, state.searchQuery, state.sortBy])

  const value = {
    ...state,
    dispatch,
    filteredClauses: getFilteredClauses(),
  }

  return (
    <ContractContext.Provider value={value}>
      {children}
    </ContractContext.Provider>
  )
}

export const useContract = () => {
  const context = useContext(ContractContext)
  if (!context) {
    throw new Error('useContract must be used within ContractProvider')
  }
  return context
}
