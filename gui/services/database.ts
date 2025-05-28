import { API_BASE_URL } from "@/config/constants"

interface DatabaseFormData {
  name: string
  type: "complete" | "minimal"
  host?: string | null
  port?: string | null
  username?: string | null
  password?: string | null
  db_name?: string | null
  schemas?: string
}

export async function createDatabase(data: DatabaseFormData) {
  try {
    console.log("Sending data to backend:", data)
    
    const response = await fetch(`${API_BASE_URL}/api/databases/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      credentials: "include",
      body: JSON.stringify(data),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => null)
      console.error("Server response:", {
        status: response.status,
        statusText: response.statusText,
        data: errorData
      })
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return await response.json()
  } catch (error) {
    console.error("Error creating database:", error)
    throw error
  }
}

// Função auxiliar para obter o cookie CSRF
function getCookie(name: string): string {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) return parts.pop()?.split(';').shift() || ''
  return ''
} 