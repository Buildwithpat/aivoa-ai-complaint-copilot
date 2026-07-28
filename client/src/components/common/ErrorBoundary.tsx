import { Component } from 'react'
import type { ErrorInfo, ReactNode } from 'react'
import { AlertTriangle } from 'lucide-react'

interface ErrorBoundaryProps {
  children: ReactNode
}

interface ErrorBoundaryState {
  hasError: boolean
}

// Last-resort fallback for unexpected render errors so a bug never blanks
// the whole app — reliability, not a new feature.
class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { hasError: false }

  static getDerivedStateFromError(): ErrorBoundaryState {
    return { hasError: true }
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    console.error('Unhandled UI error:', error, info)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex h-screen flex-col items-center justify-center gap-3 bg-gray-50 px-6 text-center">
          <span className="flex h-12 w-12 items-center justify-center rounded-full bg-rose-50 text-rose-500">
            <AlertTriangle size={22} strokeWidth={2} aria-hidden="true" />
          </span>
          <p className="text-sm font-semibold text-gray-800">Something went wrong.</p>
          <p className="max-w-sm text-sm text-gray-500">
            Please refresh the page. If the problem continues, try again in a moment.
          </p>
        </div>
      )
    }
    return this.props.children
  }
}

export default ErrorBoundary
