import { AlertCircle } from 'lucide-react'

export default function ErrorBanner({ message }) {
  return (
    <div className="card bg-red-950/20 border-red-800/50 p-4 flex items-center gap-3">
      <AlertCircle className="w-5 h-5 text-critical flex-shrink-0" />
      <p className="text-sm text-critical">{message}</p>
    </div>
  )
}
