// Type definitions matching the AI JSON contract defined in PROJECT_CONTEXT.md.
// The complaint form is read-only and always reflects this shape — the AI
// owns the data, Redux is the single source of truth.

export type Severity = 'Critical' | 'Major' | 'Minor' | 'Not Assessed'
export type Priority = 'Urgent' | 'High' | 'Medium' | 'Low' | 'Not Assessed'
export type ComplaintStatus =
  | 'Draft'
  | 'Under Investigation'
  | 'Pending CAPA'
  | 'Closed'
export type RiskLevel = 'High' | 'Medium' | 'Low' | 'Not Assessed'

export interface Complaint {
  id?: string
  customerName?: string
  customerType?: string
  productName?: string
  strength?: string
  batchNumber?: string
  manufacturingDate?: string
  expiryDate?: string
  affectedQuantity?: number
  unitOfMeasure?: string
  complaintType?: string
  description?: string
  dateReported?: string
  severity?: Severity
  priority?: Priority
  status?: ComplaintStatus
  nextAction?: string
  createdAt?: string
  updatedAt?: string
}

export interface RiskAssessment {
  riskLevel?: RiskLevel
  rationale?: string
}

export interface Completeness {
  isComplete?: boolean
  missingFields?: string[]
}

export interface AIComplaintResponse {
  complaint: Complaint
  riskAssessment: RiskAssessment
  summary: string
  completeness: Completeness
  rootCause: string
  capa: string
  duplicateProbability: number
}

export interface ChatMessage {
  id: string
  complaintId?: string
  role: 'user' | 'assistant'
  content: string
  createdAt: string
}
