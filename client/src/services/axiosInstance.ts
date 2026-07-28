import axios from 'axios'

// No default Content-Type here: axios sets `application/json` for plain
// objects and lets the browser set `multipart/form-data` (with the correct
// boundary) for FormData automatically. A hardcoded default would break
// file uploads.
const axiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
})

export default axiosInstance

interface ApiErrorResponse {
  message?: string
}

export function extractErrorMessage(error: unknown): string {
  if (axios.isAxiosError<ApiErrorResponse>(error)) {
    return error.response?.data?.message || error.message || 'Something went wrong. Please try again.'
  }
  if (error instanceof Error) {
    return error.message
  }
  return 'Something went wrong. Please try again.'
}
