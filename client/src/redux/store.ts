import { configureStore } from '@reduxjs/toolkit'
import complaintReducer from '@/redux/slices/complaintSlice'
import chatReducer from '@/redux/slices/chatSlice'

export const store = configureStore({
  reducer: {
    complaint: complaintReducer,
    chat: chatReducer,
  },
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
