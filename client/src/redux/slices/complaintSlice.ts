import { createSlice } from '@reduxjs/toolkit'
import type { PayloadAction } from '@reduxjs/toolkit'
import type { AIComplaintResponse, Complaint, Completeness, RiskAssessment } from '@/types/complaint.types'

export type ComplaintProcessingStatus = 'idle' | 'loading' | 'succeeded' | 'failed'

export interface ComplaintState {
  complaint: Complaint
  riskAssessment: RiskAssessment
  summary: string
  completeness: Completeness
  rootCause: string
  capa: string
  duplicateProbability: number
  status: ComplaintProcessingStatus
  error: string | null
}

// Real state only — populated by the AI Copilot (chat or document
// extraction) via aiResponseReceived. Nothing here is mock data.
const initialState: ComplaintState = {
  complaint: {},
  riskAssessment: {},
  summary: '',
  completeness: {},
  rootCause: '',
  capa: '',
  duplicateProbability: 0,
  status: 'idle',
  error: null,
}

const complaintSlice = createSlice({
  name: 'complaint',
  initialState,
  reducers: {
    aiResponseReceived: (state, action: PayloadAction<AIComplaintResponse>) => {
      state.complaint = action.payload.complaint
      state.riskAssessment = action.payload.riskAssessment
      state.summary = action.payload.summary
      state.completeness = action.payload.completeness
      state.rootCause = action.payload.rootCause
      state.capa = action.payload.capa
      state.duplicateProbability = action.payload.duplicateProbability
    },
    complaintProcessingStarted: (state) => {
      state.status = 'loading'
      state.error = null
    },
    complaintProcessingSucceeded: (state) => {
      state.status = 'succeeded'
    },
    complaintProcessingFailed: (state, action: PayloadAction<string>) => {
      state.status = 'failed'
      state.error = action.payload
    },
  },
})

export const { aiResponseReceived, complaintProcessingStarted, complaintProcessingSucceeded, complaintProcessingFailed } =
  complaintSlice.actions
export default complaintSlice.reducer
