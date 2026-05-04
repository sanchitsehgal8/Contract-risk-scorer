import { useState } from 'react'
import { filterOptions, sortOptions } from '../../utils/riskUtils'
import { Search, Filter } from 'lucide-react'
import { useContract } from '../../store/ContractContext'

export default function ClauseFilterBar() {
  const { activeFilter, searchQuery, sortBy, dispatch } = useContract()

  return (
    <div className="space-y-4">
      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
        <input
          type="text"
          placeholder="Search clauses..."
          className="w-full pl-10 pr-4 py-2.5 bg-surface border border-border rounded-lg text-text text-sm focus:outline-none focus:border-blue transition-colors"
          value={searchQuery}
          onChange={(e) => dispatch({ type: 'SET_SEARCH', payload: e.target.value })}
        />
      </div>

      {/* Filter & Sort */}
      <div className="grid grid-cols-2 gap-3">
        <select
          value={activeFilter}
          onChange={(e) => dispatch({ type: 'SET_FILTER', payload: e.target.value })}
          className="px-3 py-2 bg-surface border border-border rounded-lg text-sm text-text focus:outline-none focus:border-violet transition-colors"
        >
          {filterOptions.map(opt => (
            <option key={opt.value} value={opt.value} className="bg-surface text-text">
              {opt.label}
            </option>
          ))}
        </select>

        <select
          value={sortBy}
          onChange={(e) => dispatch({ type: 'SET_SORT', payload: e.target.value })}
          className="px-3 py-2 bg-surface border border-border rounded-lg text-sm text-text focus:outline-none focus:border-violet transition-colors"
        >
          {sortOptions.map(opt => (
            <option key={opt.value} value={opt.value} className="bg-surface text-text">
              {opt.label}
            </option>
          ))}
        </select>
      </div>
    </div>
  )
}
