import { useState, useEffect } from "react"
import { useLocation } from "react-router-dom"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"

export function TelegramOAuth() {
  const [countryCode, setCountryCode] = useState("")
  const [phoneNumber, setPhoneNumber] = useState("")
  const [isValid, setIsValid] = useState(true)
  const [otpSent, setOtpSent] = useState(false)
  const [otpCode, setOtpCode] = useState("")
  const [sessionID, setSessionID] = useState("")
  const [error, setError] = useState("")
  const location = useLocation()
  const [userID, setID] = useState("")

  const fullPhone = phoneNumber

  useEffect(() => {
    const params = new URLSearchParams(location.search)
    console.log(params)
    setID(params.get("user_id"))
    localStorage.setItem("user_id", params.get("user_id"))
  }, [location.search])


  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!phoneNumber || phoneNumber.length < 7 || phoneNumber.length > 15) {
      setIsValid(false)
      setError("Invalid phone number")
      return
    }

    const API_URL = import.meta.env.VITE_API_URL
    const res = await fetch(`${API_URL}/auth/telegram/start`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ phone: fullPhone }),
    })

    if (res.ok) {
      const data = await res.json()
      setSessionID(data.session_id)
      setOtpSent(true)
    } else {
      setError("Failed to send OTP. Try again.")
    }
  }

  const handleVerifyOtp = async () => {
    const res = await fetch("http://localhost:8000/auth/telegram/confirm", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userID, session_id: sessionID, code: otpCode }),
    })

    if (res.ok) {
      const data = await res.json()
      window.location.href = data.redirect_url
    } else {
      setError("Invalid code or error verifying.")
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <form onSubmit={handleSubmit} className="space-y-4">
        {!otpSent ? (
          <>
            <Input
              placeholder="Phone number"
              value={phoneNumber}
              onChange={(e) => setPhoneNumber(e.target.value.replace(/\D/g, ""))}
            />
            <Button type="submit" className="cursor-pointer">Send OTP</Button>
          </>
        ) : (
          <>
            <Input
              placeholder="Enter OTP code"
              value={otpCode}
              onChange={(e) => setOtpCode(e.target.value)}
            />
            <Button type="button" onClick={handleVerifyOtp}>Verify</Button>
          </>
        )}
        {error && <p className="text-red-500 text-sm">{error}</p>}
      </form>
    </div>
  )
}

