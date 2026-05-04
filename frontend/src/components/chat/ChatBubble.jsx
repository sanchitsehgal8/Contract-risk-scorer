import { useMemo, useState } from 'react'
import { motion } from 'framer-motion'

export default function ChatBubble({ message, isUser }) {
  const [isExpanded, setIsExpanded] = useState(false)
  const isLong = useMemo(() => message && message.length > 240, [message])

  return (
    <motion.div
      className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
      initial={{ opacity: 0, y: 5 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.1 }}
    >
      <div
        className={`max-w-xs lg:max-w-sm px-4 py-2 rounded-lg break-words ${
          isUser
            ? 'bg-blue text-white rounded-br-none'
            : 'bg-surface-high text-text border border-border rounded-bl-none'
        }`}
      >
        <p
          className={`text-sm leading-relaxed whitespace-pre-wrap ${!isUser && isLong && !isExpanded ? 'max-h-24 overflow-hidden' : ''}`}
        >
          {message}
        </p>
        {!isUser && isLong && (
          <button
            type="button"
            onClick={() => setIsExpanded(!isExpanded)}
            className="mt-2 text-xs text-blue hover:underline"
          >
            {isExpanded ? 'Show less' : 'Show more'}
          </button>
        )}
      </div>
    </motion.div>
  )
}
