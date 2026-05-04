import { FileText } from 'lucide-react'

export default function EmptyState({ message }) {
  return (
    <div className="card p-12 text-center">
      <div className="flex justify-center mb-4">
        <div className="p-3 bg-surface-high rounded-full">
          <FileText className="w-6 h-6 text-muted" />
        </div>
      </div>
      <p className="text-muted">{message}</p>
    </div>
  )
}
