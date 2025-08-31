import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { GoogleOAuth } from '@/pages/googleOAuth'
import { TelegramOAuth } from '@/pages/telegramOAuth'
import RAGChat from '@/pages/searchPage'
import { LoadingPage } from '@/pages/LoadingPage'
const App = () => (
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<GoogleOAuth />} />
      <Route path="/telegram-auth" element={<TelegramOAuth />} />
      <Route path="/loading" element={<LoadingPage />} />
      <Route path="/home" element={<RAGChat />} />
    </Routes>
  </BrowserRouter>
)

export default App

