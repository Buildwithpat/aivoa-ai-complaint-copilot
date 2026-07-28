import type { ReactNode } from 'react'
import Header from '@/components/layout/Header'

interface MainLayoutProps {
  complaintFormSlot: ReactNode
  documentUploadSlot: ReactNode
  riskAssessmentSlot: ReactNode
  chatSlot: ReactNode
}

// Reusable two-column shell: complaint form on the left, AI Copilot
// (document upload, risk assessment, chat) on the right, per the UI Layout
// spec in PROJECT_CONTEXT.md.
//
// Height chain: h-screen (root) -> main is a flex sibling of the fixed
// Header, so it takes exactly the remaining space (flex-1 + min-h-0, no
// arbitrary vh math needed) -> each column is a grid cell of that same
// fixed height. Below `lg` there's a single stacked column and the page
// itself scrolls (natural mobile behavior); at `lg` and up the two columns
// become independent scroll regions so neither can scroll the other.
//
// The right column scrolls as a unit (rather than only relying on chat's
// own internal flex-shrink) because its content — document upload + a
// variable-length AI risk assessment + chat — routinely exceeds a normal
// 1080p viewport's height. Chat keeps a real minimum height (see
// HomePage.tsx) so it settles at a usable size and the column scrolls to
// reveal it, instead of chat being squeezed toward invisible.
function MainLayout({ complaintFormSlot, documentUploadSlot, riskAssessmentSlot, chatSlot }: MainLayoutProps) {
  return (
    <div className="flex h-screen flex-col bg-gray-50">
      <Header />
      <main className="grid flex-1 grid-cols-1 gap-4 overflow-y-auto p-4 lg:min-h-0 lg:grid-cols-2 lg:overflow-hidden">
        <section className="thin-scrollbar lg:min-h-0 lg:overflow-y-auto">{complaintFormSlot}</section>

        <section className="thin-scrollbar flex flex-col gap-4 lg:min-h-0 lg:overflow-y-auto">
          {documentUploadSlot}
          {riskAssessmentSlot}
          {chatSlot}
        </section>
      </main>
    </div>
  )
}

export default MainLayout
