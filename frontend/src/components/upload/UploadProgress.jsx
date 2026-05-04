export default function UploadProgress() {
  return (
    <div className="space-y-4">
      <div className="flex justify-center">
        <div className="relative w-16 h-16">
          <div className="absolute inset-0 border-4 border-blue/20 rounded-full" />
          <div className="absolute inset-0 border-4 border-transparent border-t-blue rounded-full animate-spin" />
        </div>
      </div>
      <div>
        <p className="text-lg font-semibold text-text mb-1">Analyzing contract...</p>
        <p className="text-sm text-muted">
          Parsing PDF, detecting clauses, and scoring risks
        </p>
      </div>
    </div>
  )
}
