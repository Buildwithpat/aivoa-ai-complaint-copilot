import axiosInstance from '@/services/axiosInstance'
import type { AIComplaintResponse } from '@/types/complaint.types'

// Uploads the file as-is; the backend extracts text (PDF/DOCX/TXT/EML) and
// runs it through the same LangGraph workflow as chat.
export async function extractDocument(file: File, complaintId?: string): Promise<AIComplaintResponse> {
  const formData = new FormData()
  formData.append('file', file)
  if (complaintId) formData.append('complaint_id', complaintId)

  const { data } = await axiosInstance.post<AIComplaintResponse>('/documents/upload', formData)
  return data
}
