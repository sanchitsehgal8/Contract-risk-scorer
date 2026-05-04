import { Link } from 'react-router-dom'
import { BarChart3, Github } from 'lucide-react'

export default function Navbar() {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-bg/80 backdrop-blur-xl border-b border-border">
      <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
          <div className="p-2 bg-gradient-to-br from-blue to-blue-light rounded-lg">
            <BarChart3 className="w-5 h-5 text-white" />
          </div>
          <span className="font-bold text-lg text-text">Contract Scorer</span>
        </Link>

        <div className="flex items-center gap-4">
          <a
            href="https://github.com"
            className="p-2 hover:bg-surface rounded-lg transition-colors"
            target="_blank"
            rel="noopener noreferrer"
          >
            <Github className="w-5 h-5 text-muted hover:text-text transition-colors" />
          </a>
        </div>
      </div>
    </nav>
  )
}
