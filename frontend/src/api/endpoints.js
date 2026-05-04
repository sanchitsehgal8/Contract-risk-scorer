import client from './client'

export const analyzeContract = async (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return client.post('/api/v1/contract/analyze', formData)
}

export const getClauses = async (contractId) => {
  return client.get(`/api/v1/contract/${contractId}/clauses`)
}

export const getOrCreateSession = async (contractId) => {
  return client.get(`/api/v1/contract/${contractId}/session`)
}

export const getContractSummary = async (contractId) => {
  return client.get(`/api/v1/contract/${contractId}/summary`)
}

export const sendMessage = async (sessionId, message) => {
  return client.post(`/api/v1/chat/${sessionId}/message`, { message })
}

export const downloadReport = async (contractId) => {
  try {
    const response = await client.get(`/api/v1/contract/${contractId}/report`, {
      responseType: 'blob',
      timeout: 60000,
    })
    
    const url = URL.createObjectURL(new Blob([response], { type: 'application/pdf' }))
    const a = document.createElement('a')
    a.href = url
    a.download = `contract-risk-report-${contractId}.pdf`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    return true
  } catch (error) {
    throw error
  }
}

export const deleteSession = async (sessionId) => {
  return client.delete(`/api/v1/chat/${sessionId}`)
}

export const checkHealth = async () => {
  return client.get('/api/v1/health')
}
