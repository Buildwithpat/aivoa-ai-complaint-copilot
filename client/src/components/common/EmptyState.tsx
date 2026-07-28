import type { LucideIcon } from 'lucide-react'

interface EmptyStateProps {
  icon: LucideIcon
  title: string
  description?: string
}

function EmptyState({ icon: Icon, title, description }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 py-10 text-center">
      <span className="flex h-10 w-10 items-center justify-center rounded-full bg-gray-100 text-gray-400">
        <Icon size={18} strokeWidth={1.75} aria-hidden="true" />
      </span>
      <p className="text-sm font-medium text-gray-600">{title}</p>
      {description && <p className="max-w-xs text-xs leading-relaxed text-gray-400">{description}</p>}
    </div>
  )
}

export default EmptyState
