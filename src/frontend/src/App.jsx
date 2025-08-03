
import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { GoogleOAuth } from '@/pages/googleOAuth'
import { TelegramOAuth } from '@/pages/telegramOAuth'
import { SearchPage } from '@/pages/searchPage'
const App = () => (
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<GoogleOAuth />} />
      <Route path="/telegram-auth" element={<TelegramOAuth />} />
      <Route path="/home" element={<SearchPage />} />
    </Routes>
  </BrowserRouter>
)

export default App

