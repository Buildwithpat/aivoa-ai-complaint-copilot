import { Link } from 'react-router-dom'

function NotFoundPage() {
  return (
    <div className="flex h-screen flex-col items-center justify-center gap-3 bg-gray-50 px-6 text-center">
      <p className="text-sm text-gray-500">404 — Page not found.</p>
      <Link
        to="/"
        className="rounded-lg px-3 py-1.5 text-sm font-medium text-blue-600 outline-none transition-colors hover:bg-blue-50 focus-visible:ring-2 focus-visible:ring-blue-400"
      >
        Back to the Complaint Copilot
      </Link>
    </div>
  )
}

export default NotFoundPage
