import MainLayout from '@/components/layout/MainLayout'
import ComplaintForm from '@/features/complaint-form/ComplaintForm'
import DocumentUploadCard from '@/features/ai-copilot/DocumentUploadCard'
import RiskAssessmentCard from '@/features/ai-copilot/RiskAssessmentCard'
import ChatPanel from '@/features/ai-copilot/ChatPanel'

function HomePage() {
  return (
    <MainLayout
      complaintFormSlot={<ComplaintForm />}
      documentUploadSlot={<DocumentUploadCard />}
      riskAssessmentSlot={<RiskAssessmentCard />}
      chatSlot={<ChatPanel className="min-h-105 lg:flex-1 lg:overflow-hidden" />}
    />
  )
}

export default HomePage
