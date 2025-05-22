"use client"

import { createContext, useContext, useState, useEffect, type ReactNode } from "react"

type User = {
  id: string
  name: string
  email: string
}

type AuthContextType = {
  user: User | null
  login: (email: string, password: string) => Promise<boolean>
  register: (name: string, email: string, password: string) => Promise<boolean>
  logout: () => void
  isLoading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Carregar usuário do localStorage ao iniciar
  useEffect(() => {
    const storedUser = localStorage.getItem("user")
    if (storedUser) {
      setUser(JSON.parse(storedUser))
    }
    setIsLoading(false)
  }, [])

  // Função de login
  const login = async (email: string, password: string) => {
    setIsLoading(true)
    try {
      // Simulando uma verificação de login
      // Em um app real, isso seria uma chamada à API
      const storedUsers = JSON.parse(localStorage.getItem("users") || "[]")
      const foundUser = storedUsers.find((u: any) => u.email === email && u.password === password)

      if (!foundUser) {
        setIsLoading(false)
        return false
      }

      // Remover a senha antes de armazenar no estado
      const { password: _, ...userWithoutPassword } = foundUser
      setUser(userWithoutPassword)
      localStorage.setItem("user", JSON.stringify(userWithoutPassword))
      setIsLoading(false)
      return true
    } catch (error) {
      console.error("Erro ao fazer login:", error)
      setIsLoading(false)
      return false
    }
  }

  // Função de registro
  const register = async (name: string, email: string, password: string) => {
    setIsLoading(true)
    try {
      // Simulando um registro
      // Em um app real, isso seria uma chamada à API
      const storedUsers = JSON.parse(localStorage.getItem("users") || "[]")

      // Verificar se o email já está em uso
      if (storedUsers.some((u: any) => u.email === email)) {
        setIsLoading(false)
        return false
      }

      // Criar novo usuário
      const newUser = {
        id: Date.now().toString(),
        name,
        email,
        password,
      }

      // Adicionar à "base de dados"
      storedUsers.push(newUser)
      localStorage.setItem("users", JSON.stringify(storedUsers))

      // Fazer login automaticamente
      const { password: _, ...userWithoutPassword } = newUser
      setUser(userWithoutPassword)
      localStorage.setItem("user", JSON.stringify(userWithoutPassword))

      setIsLoading(false)
      return true
    } catch (error) {
      console.error("Erro ao registrar:", error)
      setIsLoading(false)
      return false
    }
  }

  // Função de logout
  const logout = () => {
    setUser(null)
    localStorage.removeItem("user")
  }

  return <AuthContext.Provider value={{ user, login, register, logout, isLoading }}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth deve ser usado dentro de um AuthProvider")
  }
  return context
}
