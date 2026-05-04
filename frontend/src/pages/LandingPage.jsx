import { useNavigate } from 'react-router-dom'
import { useDropzone } from 'react-dropzone'
import { useCallback } from 'react'
import { Upload, Zap, FileText, BarChart3, MessageSquare } from 'lucide-react'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import { useAnalyze } from '../hooks/useAnalyze'
import { useContract } from '../store/ContractContext'
import UploadProgress from '../components/upload/UploadProgress'

export default function LandingPage() {
  const navigate = useNavigate()
  const { analyze } = useAnalyze()
  const { isAnalyzing, analyzeError } = useContract()

  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length === 0) {
      toast.error('Please drop a PDF file')
      return
    }

    const file = acceptedFiles[0]
    if (!file.name.endsWith('.pdf')) {
      toast.error('Only PDF files are supported')
      return
    }

    try {
      const loadingToast = toast.loading('Analyzing contract...')
      const response = await analyze(file)
      toast.dismiss(loadingToast)
      toast.success('Contract analyzed successfully')
      navigate(`/analysis/${response.contract_id}`)
    } catch (error) {
      toast.error(error.message || 'Failed to analyze contract')
    }
  }, [analyze, navigate])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    disabled: isAnalyzing,
  })

  const features = [
    {
      icon: <FileText className="w-6 h-6" />,
      title: 'PDF Parsing',
      description: 'Intelligent extraction and clause detection'
    },
    {
      icon: <BarChart3 className="w-6 h-6" />,
      title: 'Risk Analysis',
      description: 'AI-powered scoring against legal precedents'
    },
    {
      icon: <MessageSquare className="w-6 h-6" />,
      title: 'Smart Chat',
      description: 'Ask questions about your contract'
    },
  ]

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.08,
        delayChildren: 0.2,
      },
    },
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 24 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.4, ease: [0.25, 0.1, 0.25, 1] },
    },
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-bg via-surface to-bg overflow-hidden">
      {/* Background elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-96 h-96 bg-blue/5 rounded-full blur-3xl" />
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-blue/3 rounded-full blur-3xl" />
      </div>

      <motion.div
        className="relative z-10 max-w-6xl mx-auto px-6 py-20"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Header */}
        <motion.div className="text-center mb-16" variants={itemVariants}>
          <div className="inline-flex items-center gap-2 mb-4 px-4 py-2 bg-surface border border-border rounded-full">
            <Zap className="w-4 h-4 text-blue" />
            <span className="text-sm font-medium text-text">World's First AI Legal Risk Scorer</span>
          </div>
          <h1 className="text-5xl md:text-7xl font-bold text-text mb-4">
            Contract Risk<br />
            <span className="bg-gradient-to-r from-blue to-blue-light bg-clip-text text-transparent">
              Scoring
            </span>
          </h1>
          <p className="text-lg text-muted max-w-2xl mx-auto">
            Upload your contract. Get instant AI-powered risk analysis with legal precedents, benchmark comparisons, and actionable insights.
          </p>
        </motion.div>

        {/* Upload zone */}
        <motion.div variants={itemVariants} className="mb-20">
          <div
            {...getRootProps()}
            className={`card p-12 text-center cursor-pointer transition-all duration-200 ${
              isDragActive ? 'border-blue/60 bg-surface-high' : 'hover:border-blue/40'
            } ${isAnalyzing ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            <input {...getInputProps()} />
            {isAnalyzing ? (
              <UploadProgress />
            ) : (
              <div className="space-y-4">
                <div className="flex justify-center">
                  <div className="p-4 bg-blue/10 rounded-full">
                    <Upload className="w-8 h-8 text-blue" />
                  </div>
                </div>
                <div>
                  <p className="text-lg font-semibold text-text mb-1">
                    {isDragActive ? 'Drop PDF here' : 'Drag & drop your PDF'}
                  </p>
                  <p className="text-sm text-muted">or click to select</p>
                </div>
              </div>
            )}
          </div>
          {analyzeError && (
            <p className="text-critical text-sm mt-3">{analyzeError}</p>
          )}
        </motion.div>

        {/* Features */}
        <motion.div className="grid md:grid-cols-3 gap-6" variants={itemVariants}>
          {features.map((feature, i) => (
            <motion.div
              key={i}
              className="card p-6 group hover:bg-surface-high transition-all"
              variants={itemVariants}
            >
              <div className="p-3 bg-blue/10 rounded-lg w-fit mb-4 group-hover:bg-blue/20 transition-colors">
                <div className="text-blue">{feature.icon}</div>
              </div>
              <h3 className="font-semibold text-text mb-2">{feature.title}</h3>
              <p className="text-sm text-muted">{feature.description}</p>
            </motion.div>
          ))}
        </motion.div>
      </motion.div>
    </div>
  )
}
