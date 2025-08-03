import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { GoogleOAuthProvider } from '@react-oauth/google'
import './index.css'
import App from './App.jsx'

const ClientId = import.meta.env.VITE_REACT_APP_CLIENT_ID

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <GoogleOAuthProvider clientId={ClientId}>
      <App />
    </GoogleOAuthProvider>
  </StrictMode>,
)
