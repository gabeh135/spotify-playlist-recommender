import { useState, useEffect } from "react"

const STORAGE_KEY = "playlist_user_id"
const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000"

export function useUser() {
  const [userId, setUserId] = useState<string | null>(null)

  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
      setUserId(stored)
      return
    }

    fetch(`${BASE_URL}/users`, { method: "POST" })
      .then((res) => res.json())
      .then((data: { user_id: string }) => {
        localStorage.setItem(STORAGE_KEY, data.user_id)
        setUserId(data.user_id)
      })
  }, [])

  return userId
}
