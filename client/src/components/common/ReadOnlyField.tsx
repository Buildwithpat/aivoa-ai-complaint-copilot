import { memo } from 'react'
import type { LucideIcon } from 'lucide-react'

interface ReadOnlyFieldProps {
  id: string
  label: string
  value?: string
  icon?: LucideIcon
  span?: 'full' | 'half'
  multiline?: boolean
}

// Every complaint field is rendered read-only: the AI Copilot owns this
// data, the form never accepts manual input. Uses role="group" +
// aria-labelledby (rather than a real <label>) since there is no form
// control to associate a label with.
function ReadOnlyField({ id, label, value, icon: Icon, span = 'half', multiline = false }: ReadOnlyFieldProps) {
  const labelId = `${id}-label`

  return (
    <div className={span === 'full' ? 'col-span-2' : 'col-span-2 sm:col-span-1'}>
      <span id={labelId} className="mb-1.5 flex items-center gap-1.5 text-xs font-medium text-gray-500">
        {Icon && <Icon size={13} strokeWidth={2} className="text-gray-400" aria-hidden="true" />}
        {label}
      </span>
      <div
        role="group"
        aria-labelledby={labelId}
        className={`w-full rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm text-gray-800 ${
          multiline ? 'min-h-20 whitespace-pre-wrap break-words' : 'truncate'
        }`}
        title={value}
      >
        {value || <span className="text-gray-400">—</span>}
      </div>
    </div>
  )
}

export default memo(ReadOnlyField)
