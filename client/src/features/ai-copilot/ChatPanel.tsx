import { useEffect, useRef, useState } from 'react'
import type { KeyboardEvent } from 'react'
import { MessageSquare, SendHorizonal } from 'lucide-react'
import { toast } from 'sonner'
import Card from '@/components/common/Card'
import TypingIndicator from '@/components/common/TypingIndicator'
import ChatMessageBubble from '@/features/ai-copilot/ChatMessageBubble'
import { useAppDispatch, useAppSelector } from '@/redux/hooks'
import { messageAdded, messageRemoved, sendingStatusChanged } from '@/redux/slices/chatSlice'
import {
  aiResponseReceived,
  complaintProcessingFailed,
  complaintProcessingStarted,
  complaintProcessingSucceeded,
} from '@/redux/slices/complaintSlice'
import { sendChatMessage } from '@/services/chatService'
import { extractErrorMessage } from '@/services/axiosInstance'

const MAX_MESSAGE_LENGTH = 4000
const LENGTH_WARNING_THRESHOLD = MAX_MESSAGE_LENGTH - 200

interface ChatPanelProps {
  // Sizing/positioning is the parent layout's concern (see MainLayout) —
  // ChatPanel itself only knows how to lay out its own header/list/input.
  className?: string
}

// Every send goes through /api/chat, which runs the LangGraph workflow and
// returns both chat messages and the updated structured complaint — Redux
// is updated from that single response, never from local guesses.
function ChatPanel({ className = '' }: ChatPanelProps) {
  const dispatch = useAppDispatch()
  const messages = useAppSelector((state) => state.chat.messages)
  const isSending = useAppSelector((state) => state.chat.isSending)
  const complaintId = useAppSelector((state) => state.complaint.complaint.id)
  const complaintStatus = useAppSelector((state) => state.complaint.status)
  const [draft, setDraft] = useState('')
  const scrollRef = useRef<HTMLDivElement>(null)

  // Guards against a chat send and a document upload racing each other:
  // both read `complaintId` from Redux before their request resolves, so if
  // both fired at once they could each create a separate complaint instead
  // of updating the same one.
  const isBusy = isSending || complaintStatus === 'loading'

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages, isSending])

  const handleSend = async () => {
    const content = draft.trim()
    if (!content || isBusy || content.length > MAX_MESSAGE_LENGTH) return

    const optimisticId = `local-${Date.now()}`
    dispatch(
      messageAdded({
        id: optimisticId,
        role: 'user',
        content,
        createdAt: new Date().toISOString(),
      }),
    )
    setDraft('')
    dispatch(sendingStatusChanged(true))
    dispatch(complaintProcessingStarted())

    try {
      const response = await sendChatMessage(content, complaintId)
      dispatch(messageRemoved(optimisticId))
      dispatch(messageAdded(response.userMessage))
      dispatch(messageAdded(response.assistantMessage))
      dispatch(aiResponseReceived(response.aiResponse))
      dispatch(complaintProcessingSucceeded())
    } catch (error) {
      dispatch(messageRemoved(optimisticId))
      setDraft(content)
      const message = extractErrorMessage(error)
      dispatch(complaintProcessingFailed(message))
      toast.error(message)
    } finally {
      dispatch(sendingStatusChanged(false))
    }
  }

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      handleSend()
    }
  }

  const remainingChars = MAX_MESSAGE_LENGTH - draft.length
  const isOverLimit = remainingChars < 0
  const canSend = Boolean(draft.trim()) && !isBusy && !isOverLimit

  return (
    <Card
      title="AI Copilot Chat"
      subtitle="Log or edit the complaint using natural language"
      icon={MessageSquare}
      className={`flex flex-col ${className}`.trim()}
      bodyClassName="flex min-h-0 flex-1 flex-col p-0"
    >
      <div
        ref={scrollRef}
        role="log"
        aria-live="polite"
        aria-label="Chat conversation"
        className="thin-scrollbar min-h-0 flex-1 space-y-4 overflow-y-auto px-5 py-4"
      >
        {messages.length === 0 && !isSending && (
          <p className="pt-8 text-center text-sm text-gray-400">
            Describe a complaint below to get started — e.g. "Apollo Pharmacy reported discolored capsules in
            Amoxicillin Capsules 500mg."
          </p>
        )}
        {messages.map((message) => (
          <ChatMessageBubble key={message.id} message={message} />
        ))}
        {isSending && (
          <div className="flex items-center gap-2.5">
            <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-gray-100 text-gray-500">
              <TypingIndicator />
            </span>
          </div>
        )}
      </div>

      <div className="border-t border-gray-100 p-4">
        <div className="flex items-end gap-2 rounded-xl border border-gray-200 bg-gray-50 p-2 focus-within:border-blue-300 focus-within:ring-2 focus-within:ring-blue-100">
          <textarea
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            onKeyDown={handleKeyDown}
            rows={1}
            disabled={isBusy}
            maxLength={MAX_MESSAGE_LENGTH}
            aria-label="Message the AI Copilot"
            placeholder="e.g. The batch number is BMX24602 and affected quantity is 48 capsules"
            className="max-h-28 min-h-9 flex-1 resize-none bg-transparent px-2 py-1.5 text-sm text-gray-800 placeholder:text-gray-400 focus:outline-none disabled:cursor-not-allowed"
          />
          <button
            type="button"
            onClick={handleSend}
            disabled={!canSend}
            aria-busy={isSending}
            className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-blue-600 text-white outline-none transition-colors duration-150 hover:bg-blue-700 focus-visible:ring-2 focus-visible:ring-blue-400 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:bg-gray-200 disabled:text-gray-400"
            aria-label="Send message"
          >
            <SendHorizonal size={16} strokeWidth={2.25} />
          </button>
        </div>
        {draft.length > LENGTH_WARNING_THRESHOLD && (
          <p className={`mt-1 text-right text-[11px] ${isOverLimit ? 'text-rose-500' : 'text-gray-400'}`}>
            {remainingChars} characters remaining
          </p>
        )}
      </div>
    </Card>
  )
}

export default ChatPanel
