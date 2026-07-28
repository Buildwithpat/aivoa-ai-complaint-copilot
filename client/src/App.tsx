import { Route, Routes } from 'react-router-dom'
import { Toaster } from 'sonner'
import HomePage from '@/pages/HomePage'
import NotFoundPage from '@/pages/NotFoundPage'

function App() {
  return (
    <>
      <Toaster position="top-right" richColors closeButton />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </>
  )
}

export default App
