import ClauseCard from './ClauseCard'
import ClauseFilterBar from './ClauseFilterBar'
import EmptyState from '../shared/EmptyState'

export default function ClauseList({ clauses }) {
  return (
    <div className="space-y-4">
      <ClauseFilterBar />
      
      {clauses.length > 0 ? (
        <div className="space-y-3">
          {clauses.map(clause => (
            <ClauseCard key={clause.clause_id} clause={clause} />
          ))}
        </div>
      ) : (
        <EmptyState message="No clauses match your filters" />
      )}
    </div>
  )
}
