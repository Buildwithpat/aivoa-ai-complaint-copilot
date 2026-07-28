import type { ReactNode } from 'react'
import type { LucideIcon } from 'lucide-react'

interface CardProps {
  title?: string
  subtitle?: string
  icon?: LucideIcon
  actions?: ReactNode
  children: ReactNode
  bodyClassName?: string
  className?: string
}

function Card({ title, subtitle, icon: Icon, actions, children, bodyClassName, className = '' }: CardProps) {
  return (
    <div className={`rounded-xl border border-gray-200 bg-white shadow-sm ${className}`}>
      {(title || actions) && (
        <div className="flex items-center justify-between gap-3 border-b border-gray-100 px-5 py-4">
          <div className="flex items-center gap-2.5">
            {Icon && (
              <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-blue-50 text-blue-600">
                <Icon size={16} strokeWidth={2.25} />
              </span>
            )}
            <div>
              {title && <h2 className="text-sm font-semibold text-gray-900">{title}</h2>}
              {subtitle && <p className="text-xs text-gray-400">{subtitle}</p>}
            </div>
          </div>
          {actions}
        </div>
      )}
      <div className={bodyClassName ?? 'p-5'}>{children}</div>
    </div>
  )
}

export default Card
