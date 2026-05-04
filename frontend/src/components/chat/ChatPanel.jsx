import { useEffect, useRef } from 'react'
import { MessageSquare } from 'lucide-react'
import { useChat } from '../../hooks/useChat'
import ChatBubble from './ChatBubble'
import ChatInput from './ChatInput'
import TypingIndicator from './TypingIndicator'
import toast from 'react-hot-toast'

export default function ChatPanel({ contractId, sessionId }) {
  const { messages, isLoading, error, sendMessage } = useChat()
  const messagesEndRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'auto' })
  }, [messages])

  const handleSendMessage = async (content) => {
    if (!sessionId) {
      toast.error('Chat session not initialized')
      return
    }
    try {
      await sendMessage(sessionId, content)
    } catch (err) {
      console.error('Failed to send message:', err)
    }
  }

  return (
    <div className="card p-6 h-full min-h-96 flex flex-col bg-surface-high border border-border">
      {/* Header */}
      <div className="flex items-center gap-2 mb-4 pb-4 border-b border-border">
        <MessageSquare className="w-5 h-5 text-blue" />
        <h3 className="font-semibold text-text">Contract Assistant</h3>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-3 mb-4 min-h-0 pr-2">
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center text-center">
            <p className="text-muted text-sm">Ask questions about the contract and get instant AI-powered insights</p>
          </div>
        ) : (
          <>
            {messages.map((msg, i) => (
              <ChatBubble
                key={i}
                message={msg.content}
                isUser={msg.role === 'user'}
              />
            ))}
            {isLoading && <TypingIndicator />}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Error */}
      {error && (
        <p className="text-red-400 text-xs mb-2">{error}</p>
      )}

      {/* Input */}
      <ChatInput onSend={handleSendMessage} isLoading={isLoading || !sessionId} />
    </div>
  )
}
