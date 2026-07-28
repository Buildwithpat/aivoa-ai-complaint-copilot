import { Loader2 } from 'lucide-react'

interface SpinnerProps {
  size?: number
  className?: string
}

function Spinner({ size = 14, className = 'text-current' }: SpinnerProps) {
  return <Loader2 size={size} className={`animate-spin ${className}`} strokeWidth={2.5} />
}

export default Spinner
