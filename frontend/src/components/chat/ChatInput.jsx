import { useState } from 'react'
import { Send } from 'lucide-react'

export default function ChatInput({ onSend, isLoading }) {
  const [input, setInput] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (input.trim() && !isLoading) {
      onSend(input)
      setInput('')
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <input
        type="text"
        placeholder="Ask about the contract..."
        className="flex-1 px-4 py-2.5 bg-surface border border-border rounded-lg text-text text-sm focus:outline-none focus:border-violet transition-colors disabled:opacity-50"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        disabled={isLoading}
      />
      <button
        type="submit"
        disabled={!input.trim() || isLoading}
        className="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <Send className="w-4 h-4" />
      </button>
    </form>
  )
}
