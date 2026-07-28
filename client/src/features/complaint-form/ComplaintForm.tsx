import { ClipboardList, Lock, Zap } from 'lucide-react'
import Card from '@/components/common/Card'
import Badge from '@/components/common/Badge'
import EmptyState from '@/components/common/EmptyState'
import ReadOnlyField from '@/components/common/ReadOnlyField'
import Skeleton from '@/components/common/Skeleton'
import Spinner from '@/components/common/Spinner'
import { useAppSelector } from '@/redux/hooks'
import { COMPLAINT_FIELDS } from '@/features/complaint-form/complaintFields.config'
import { priorityTone, severityTone, statusTone } from '@/utils/badgeTone'

const SKELETON_FIELD_COUNT = COMPLAINT_FIELDS.length

// Read-only by design: the AI Copilot owns this data end-to-end. Nothing on
// this form is ever typed in manually.
function ComplaintForm() {
  const { complaint, status } = useAppSelector((state) => state.complaint)
  const hasComplaint = Boolean(complaint.id)
  const isInitialLoad = status === 'loading' && !hasComplaint
  const isUpdating = status === 'loading' && hasComplaint

  return (
    <Card
      title="Log Customer Complaint"
      subtitle="Auto-populated by the AI Copilot"
      icon={ClipboardList}
      actions={
        isUpdating ? (
          <span className="flex items-center gap-1.5 text-xs font-medium text-blue-600">
            <Spinner size={13} />
            Updating…
          </span>
        ) : (
          <span className="flex items-center gap-1.5 text-xs font-medium text-gray-400">
            <Lock size={12} strokeWidth={2.25} aria-hidden="true" />
            Read-only
          </span>
        )
      }
    >
      {isInitialLoad ? (
        <div className="grid grid-cols-2 gap-x-4 gap-y-5" aria-busy="true" aria-label="Loading complaint">
          {Array.from({ length: SKELETON_FIELD_COUNT }).map((_, index) => (
            <div key={index} className={index === 0 ? 'col-span-2' : 'col-span-2 sm:col-span-1'}>
              <Skeleton className="mb-1.5 h-3 w-20" />
              <Skeleton className="h-9 w-full" />
            </div>
          ))}
        </div>
      ) : !hasComplaint ? (
        <EmptyState
          icon={ClipboardList}
          title="No complaint logged yet"
          description="Describe a complaint in the AI Copilot chat, or upload a complaint document, to get started."
        />
      ) : (
        <>
          <div className="mb-5 flex flex-wrap items-center gap-2">
            <Badge label={`Severity: ${complaint.severity ?? 'Not Assessed'}`} tone={severityTone(complaint.severity)} />
            <Badge label={`Priority: ${complaint.priority ?? 'Not Assessed'}`} tone={priorityTone(complaint.priority)} />
            <Badge label={complaint.status ?? 'Draft'} tone={statusTone(complaint.status)} />
          </div>

          <div className="grid grid-cols-2 gap-x-4 gap-y-5">
            {COMPLAINT_FIELDS.map((field) => (
              <ReadOnlyField
                key={field.key}
                id={field.key}
                label={field.label}
                icon={field.icon}
                span={field.span}
                multiline={field.multiline}
                value={field.getValue(complaint)}
              />
            ))}

            <ReadOnlyField id="nextAction" label="Next Action" icon={Zap} span="full" multiline value={complaint.nextAction} />
          </div>

          <p className="mt-5 flex items-center gap-1.5 border-t border-gray-100 pt-4 text-xs text-gray-400">
            <Lock size={12} strokeWidth={2.25} aria-hidden="true" />
            This form is managed entirely by the AI Complaint Copilot. Use the chat panel to log or edit a complaint.
          </p>
        </>
      )}
    </Card>
  )
}

export default ComplaintForm
