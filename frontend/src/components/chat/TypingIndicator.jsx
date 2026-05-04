import { motion } from 'framer-motion'

export default function TypingIndicator() {
  const dots = [0, 1, 2]
  
  return (
    <div className="flex items-center gap-1 py-2 px-3">
      {dots.map(i => (
        <motion.div
          key={i}
          className="w-2 h-2 bg-blue rounded-full"
          animate={{ y: [0, -8, 0] }}
          transition={{
            duration: 0.6,
            repeat: Infinity,
            delay: i * 0.2
          }}
        />
      ))}
    </div>
  )
}
