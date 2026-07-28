import { memo } from 'react'
import { Bot, User } from 'lucide-react'
import type { ChatMessage } from '@/types/complaint.types'
import { formatDateTime } from '@/utils/formatters'

interface ChatMessageBubbleProps {
  message: ChatMessage
}

function ChatMessageBubble({ message }: ChatMessageBubbleProps) {
  const isUser = message.role === 'user'

  return (
    <div className={`chat-message-enter flex items-start gap-2.5 ${isUser ? 'flex-row-reverse' : ''}`}>
      <span
        className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full ${
          isUser ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-500'
        }`}
      >
        {isUser ? <User size={13} strokeWidth={2.5} /> : <Bot size={13} strokeWidth={2.5} />}
      </span>
      <div className={`flex min-w-0 max-w-[80%] flex-col gap-1 ${isUser ? 'items-end' : 'items-start'}`}>
        <div
          className={`min-w-0 break-words rounded-2xl px-3.5 py-2.5 text-sm leading-relaxed ${
            isUser
              ? 'rounded-tr-sm bg-blue-600 text-white'
              : 'rounded-tl-sm border border-gray-100 bg-gray-50 text-gray-700'
          }`}
        >
          {message.content}
        </div>
        <span className="px-1 text-[11px] text-gray-400">{formatDateTime(message.createdAt)}</span>
      </div>
    </div>
  )
}

export default memo(ChatMessageBubble)
