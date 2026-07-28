import axiosInstance from '@/services/axiosInstance'
import type { AIComplaintResponse, ChatMessage } from '@/types/complaint.types'

export interface ChatSendResponse {
  userMessage: ChatMessage
  assistantMessage: ChatMessage
  aiResponse: AIComplaintResponse
}

export async function sendChatMessage(content: string, complaintId?: string): Promise<ChatSendResponse> {
  const { data } = await axiosInstance.post<ChatSendResponse>('/chat/messages', {
    content,
    complaintId,
  })
  return data
}
