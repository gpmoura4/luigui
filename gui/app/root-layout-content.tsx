"use client"

import type React from "react"
import { useAuth } from "@/contexts/AuthContext"
import { usePathname, useRouter } from "next/navigation"
import { useEffect } from "react"
import ClientLayout from "./ClientLayout"
import AuthLayout from "./auth-layout"

export default function RootLayoutContent({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()
  const router = useRouter()
  const pathname = usePathname()

  const isAuthPage = pathname === "/login" || pathname === "/register"

  useEffect(() => {
    if (!loading) {
      // Se não estiver logado e não estiver em uma página de autenticação, redirecionar para login
      if (!user && !isAuthPage) {
        router.push("/login")
      }

      // Se estiver logado e estiver em uma página de autenticação, redirecionar para home
      if (user && isAuthPage) {
        router.push("/")
      }
    }
  }, [user, loading, router, pathname, isAuthPage])

  // Se estiver carregando, mostrar um indicador de carregamento
  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    )
  }

  // Escolher o layout apropriado com base no estado de autenticação
  if (!user && isAuthPage) {
    return <AuthLayout>{children}</AuthLayout>
  }

  // Se o usuário não estiver logado e não estiver em uma página de autenticação,
  // não renderizar nada até que o redirecionamento ocorra
  if (!user && !isAuthPage) {
    return null
  }

  // Se o usuário estiver logado, usar o layout principal com sidebar
  return <ClientLayout>{children}</ClientLayout>
}
