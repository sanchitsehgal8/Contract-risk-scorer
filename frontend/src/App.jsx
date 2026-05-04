import { Routes, Route } from 'react-router-dom'
import { useEffect } from 'react'
import Navbar from './components/layout/Navbar'
import LandingPage from './pages/LandingPage'
import AnalysisPage from './pages/AnalysisPage'
import NotFoundPage from './pages/NotFoundPage'

function App() {
  useEffect(() => {
    // Just log if backend is available, don't block UI
    const checkBackend = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/v1/health', { mode: 'no-cors' })
        console.log('✓ Backend health check passed')
      } catch (error) {
        console.warn('⚠️  Backend may not be available yet')
      }
    }

    checkBackend()
  }, [])

  return (
    <div className="min-h-screen bg-bg">
      <Navbar />
      <main className="pt-20">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/analysis/:contractId" element={<AnalysisPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
