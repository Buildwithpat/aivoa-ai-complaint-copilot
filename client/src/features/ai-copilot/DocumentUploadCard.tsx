import { useRef, useState } from 'react'
import type { DragEvent, KeyboardEvent } from 'react'
import { CheckCircle2, FileUp, Upload, X } from 'lucide-react'
import { toast } from 'sonner'
import Card from '@/components/common/Card'
import Spinner from '@/components/common/Spinner'
import { useAppDispatch, useAppSelector } from '@/redux/hooks'
import {
  aiResponseReceived,
  complaintProcessingFailed,
  complaintProcessingStarted,
  complaintProcessingSucceeded,
} from '@/redux/slices/complaintSlice'
import { extractDocument } from '@/services/documentService'
import { extractErrorMessage } from '@/services/axiosInstance'

const ACCEPTED_TYPES = '.pdf,.docx,.txt,.eml'
const ALLOWED_EXTENSIONS = ['.pdf', '.docx', '.txt', '.eml']
const MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024

type UploadStatus = 'idle' | 'processing' | 'done' | 'error'

function getExtension(filename: string): string {
  const dotIndex = filename.lastIndexOf('.')
  return dotIndex === -1 ? '' : filename.slice(dotIndex).toLowerCase()
}

function validateFile(file: File): string | null {
  const extension = getExtension(file.name)
  if (!ALLOWED_EXTENSIONS.includes(extension)) {
    return `"${extension || 'unknown'}" files aren't supported. Use PDF, DOCX, TXT, or EML.`
  }
  if (file.size === 0) {
    return 'That file is empty.'
  }
  if (file.size > MAX_FILE_SIZE_BYTES) {
    return 'That file is larger than the 10MB upload limit.'
  }
  return null
}

// Uploads the dropped/selected file to /api/documents/upload, which
// extracts its text server-side and runs it through the same LangGraph
// workflow chat uses.
function DocumentUploadCard() {
  const dispatch = useAppDispatch()
  const complaintId = useAppSelector((state) => state.complaint.complaint.id)
  const complaintStatus = useAppSelector((state) => state.complaint.status)
  const inputRef = useRef<HTMLInputElement>(null)
  const [fileName, setFileName] = useState<string | null>(null)
  const [status, setStatus] = useState<UploadStatus>('idle')
  const [isDragging, setIsDragging] = useState(false)
  // Also blocks on the global complaint status, not just this component's
  // own `status` — otherwise a chat send in flight and a document upload
  // could race, each reading the same stale `complaintId` and creating two
  // separate complaints instead of updating one.
  const isBusy = status === 'processing' || complaintStatus === 'loading'

  const processFile = async (file: File) => {
    if (isBusy) return

    const validationError = validateFile(file)
    if (validationError) {
      toast.error(validationError)
      return
    }

    setFileName(file.name)
    setStatus('processing')
    dispatch(complaintProcessingStarted())

    try {
      const aiResponse = await extractDocument(file, complaintId)
      dispatch(aiResponseReceived(aiResponse))
      dispatch(complaintProcessingSucceeded())
      setStatus('done')
      toast.success('Document processed — complaint form updated.')
    } catch (error) {
      const message = extractErrorMessage(error)
      dispatch(complaintProcessingFailed(message))
      setStatus('error')
      toast.error(message)
    }
  }

  const openFilePicker = () => {
    if (!isBusy) inputRef.current?.click()
  }

  const handleDrop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    setIsDragging(false)
    if (isBusy) return
    const file = event.dataTransfer.files?.[0]
    if (file) void processFile(file)
  }

  const handleKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault()
      openFilePicker()
    }
  }

  const clearFile = () => {
    setFileName(null)
    setStatus('idle')
    if (inputRef.current) inputRef.current.value = ''
  }

  return (
    <Card title="Document Extraction" subtitle="PDF, DOCX, TXT or EML" icon={FileUp}>
      <div
        role="button"
        tabIndex={0}
        aria-label="Upload a complaint document"
        aria-disabled={isBusy}
        aria-busy={isBusy}
        onClick={openFilePicker}
        onKeyDown={handleKeyDown}
        onDragOver={(event) => {
          event.preventDefault()
          if (!isBusy) setIsDragging(true)
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        className={`flex flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed px-4 py-6 text-center outline-none transition-colors duration-200 focus-visible:ring-2 focus-visible:ring-blue-400 focus-visible:ring-offset-2 ${
          isBusy
            ? 'cursor-not-allowed border-gray-200 bg-gray-50 opacity-60'
            : isDragging
              ? 'cursor-pointer border-blue-400 bg-blue-50'
              : 'cursor-pointer border-gray-200 bg-gray-50 hover:border-blue-300 hover:bg-blue-50/50'
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPTED_TYPES}
          className="hidden"
          disabled={isBusy}
          onChange={(event) => {
            const file = event.target.files?.[0]
            if (file) void processFile(file)
          }}
        />
        <Upload size={20} strokeWidth={1.75} className="text-blue-500" aria-hidden="true" />
        <p className="text-sm font-medium text-gray-700">Drop a complaint document, or click to browse</p>
        <p className="text-xs text-gray-400">Supported formats: PDF, DOCX, TXT, EML (max 10MB)</p>
      </div>

      {fileName && (
        <div className="mt-3 flex items-center justify-between gap-3 rounded-lg border border-gray-200 bg-white px-3 py-2.5">
          <div className="flex min-w-0 items-center gap-2.5">
            {status === 'processing' ? (
              <Spinner size={16} className="shrink-0 text-blue-500" />
            ) : (
              <CheckCircle2
                size={16}
                className={`shrink-0 ${status === 'error' ? 'text-rose-500' : 'text-emerald-500'}`}
                strokeWidth={2.25}
                aria-hidden="true"
              />
            )}
            <div className="min-w-0">
              <p className="truncate text-sm font-medium text-gray-800">{fileName}</p>
              <p className="text-xs text-gray-400" aria-live="polite">
                {status === 'processing' && 'Extracting and analyzing…'}
                {status === 'done' && 'Complaint form updated from this document.'}
                {status === 'error' && 'Failed to process this document.'}
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={clearFile}
            disabled={isBusy}
            className="shrink-0 rounded-md p-1 text-gray-400 outline-none transition-colors hover:bg-gray-100 hover:text-gray-600 focus-visible:ring-2 focus-visible:ring-blue-400 disabled:cursor-not-allowed disabled:opacity-50"
            aria-label="Remove file"
          >
            <X size={15} />
          </button>
        </div>
      )}
    </Card>
  )
}

export default DocumentUploadCard
