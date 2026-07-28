import { createSlice } from '@reduxjs/toolkit'
import type { PayloadAction } from '@reduxjs/toolkit'
import type { ChatMessage } from '@/types/complaint.types'

export interface ChatState {
  messages: ChatMessage[]
  isSending: boolean
}

// Real state only — the conversation starts empty and is populated by
// actual /api/chat calls. No mock messages.
const initialState: ChatState = {
  messages: [],
  isSending: false,
}

const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    messageAdded: (state, action: PayloadAction<ChatMessage>) => {
      state.messages.push(action.payload)
    },
    messageRemoved: (state, action: PayloadAction<string>) => {
      state.messages = state.messages.filter((message) => message.id !== action.payload)
    },
    sendingStatusChanged: (state, action: PayloadAction<boolean>) => {
      state.isSending = action.payload
    },
  },
})

export const { messageAdded, messageRemoved, sendingStatusChanged } = chatSlice.actions
export default chatSlice.reducer
