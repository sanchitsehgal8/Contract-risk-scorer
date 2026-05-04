export default function NotFoundPage() {
  return (
    <div className="min-h-screen flex items-center justify-center px-6">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-text mb-4">404</h1>
        <p className="text-xl text-muted mb-8">Page not found</p>
        <a href="/" className="btn btn-primary">
          Back to Home
        </a>
      </div>
    </div>
  )
}
