import { ShieldCheck } from 'lucide-react'
import { useAppSelector } from '@/redux/hooks'

function Header() {
  const complaintId = useAppSelector((state) => state.complaint.complaint.id)

  return (
    <header className="flex h-16 shrink-0 items-center justify-between border-b border-gray-200 bg-white px-6">
      <div className="flex items-center gap-3">
        <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-600 text-white shadow-sm shadow-blue-200">
          <ShieldCheck size={18} strokeWidth={2.25} />
        </span>
        <div>
          <p className="text-sm font-semibold leading-tight text-gray-900">AIVOA AI Complaint Copilot</p>
          <p className="text-xs leading-tight text-gray-400">Pharmaceutical Complaint Intake</p>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {complaintId && (
          <span className="hidden rounded-full bg-gray-100 px-3 py-1 text-xs font-medium text-gray-500 sm:inline-block">
            {complaintId}
          </span>
        )}
        <span className="flex items-center gap-1.5 rounded-full bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700 ring-1 ring-inset ring-emerald-600/20">
          <span aria-hidden="true" className="relative flex h-1.5 w-1.5">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
            <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-emerald-500" />
          </span>
          AI Assistant Active
        </span>
      </div>
    </header>
  )
}

export default Header
