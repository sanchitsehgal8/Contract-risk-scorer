import { useState } from 'react'
import { sendMessage as sendChatMessage } from '../api/endpoints'

export const useChat = () => {
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  const sendMessage = async (sessionId, content) => {
    if (!sessionId) return
    setIsLoading(true)
    setError(null)

    try {
      const response = await sendChatMessage(sessionId, content)
      setMessages(prev => [
        ...prev,
        { role: 'user', content },
        {
          role: 'assistant',
          content: response.answer,
          references: response.referenced_clauses
        }
      ])
      return response
    } catch (err) {
      setError(err.message)
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  return { messages, isLoading, error, sendMessage }
}
