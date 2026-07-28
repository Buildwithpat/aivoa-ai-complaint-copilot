interface ProgressBarProps {
  percentage: number
  tone?: 'blue' | 'amber' | 'rose' | 'emerald'
}

const TONE_CLASSES: Record<NonNullable<ProgressBarProps['tone']>, string> = {
  blue: 'bg-blue-600',
  amber: 'bg-amber-500',
  rose: 'bg-rose-500',
  emerald: 'bg-emerald-500',
}

function ProgressBar({ percentage, tone = 'blue' }: ProgressBarProps) {
  const clamped = Math.min(100, Math.max(0, percentage))
  return (
    <div className="h-2 w-full overflow-hidden rounded-full bg-gray-100">
      <div
        className={`h-full rounded-full transition-all duration-500 ease-out ${TONE_CLASSES[tone]}`}
        style={{ width: `${clamped}%` }}
      />
    </div>
  )
}

export default ProgressBar
