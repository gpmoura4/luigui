"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Users, Layers, Eye, Database, ChevronLeft, ChevronRight, Plus, LogOut } from "lucide-react"
import Link from "next/link"
import { usePathname, useRouter } from "next/navigation"
import { cn } from "@/lib/utils"
import { useAuth } from "@/contexts/AuthContext"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

export default function ClientLayout({ children }: { children: React.ReactNode }) {
  const [collapsed, setCollapsed] = useState(false)
  const pathname = usePathname()
  const { user, logout, isAuthenticated, loading } = useAuth()
  const router = useRouter()

  // Adicionar verificação de autenticação
  useEffect(() => {
    if (!loading) {  // Só verifica após carregar o estado de autenticação
      if (!isAuthenticated && pathname !== '/auth/login') {
        router.push('/auth/login')
      } else if (isAuthenticated && pathname === '/auth/login') {
        router.push('/')
      }
    }
  }, [isAuthenticated, loading, pathname, router])

  // Se estiver carregando ou não estiver autenticado, mostra loading ou nada
  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (!isAuthenticated && pathname !== '/auth/login') {
    return null
  }

  // Carregar o estado de colapso do localStorage ao montar o componente
  useEffect(() => {
    const savedState = localStorage.getItem("sidebar-collapsed")
    if (savedState !== null) {
      setCollapsed(savedState === "true")
    }
  }, [])

  // Salvar o estado de colapso no localStorage quando ele mudar
  useEffect(() => {
    localStorage.setItem("sidebar-collapsed", String(collapsed))
  }, [collapsed])

  const toggleSidebar = () => {
    setCollapsed(!collapsed)
  }

  const handleLogout = async () => {
    await logout()
    router.push("/auth/login")
  }

  // Obter as iniciais do nome do usuário
  const getInitials = (name: string | undefined) => {
    if (!name) return ""
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
      .substring(0, 2)
  }

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <div
        className={cn(
          "border-r bg-muted/10 transition-all duration-300 ease-in-out relative",
          collapsed ? "w-16" : "w-64",
        )}
      >
        <div className="px-4 border-b flex items-center justify-between h-14">
          <div className={cn("flex items-center gap-2", collapsed && "justify-center")}>
            <div className="h-6 w-6 rounded-full bg-gradient-to-r from-teal-400 to-primary flex-shrink-0" />
            {!collapsed && <span className="font-semibold">Luigui</span>}
          </div>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={toggleSidebar}
            title={collapsed ? "Expandir menu" : "Recolher menu"}
          >
            {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          </Button>
        </div>

        {/* Botão Nova Consulta */}
        <div className="p-4 border-b">
          <Button
            variant="default"
            className={cn("w-full gap-2", collapsed ? "justify-center px-0" : "justify-center")}
            asChild
          >
            <Link href="/" title="Nova Consulta">
              <Plus className="h-4 w-4" />
              {!collapsed && <span>Nova Consulta</span>}
            </Link>
          </Button>
        </div>

        <ScrollArea className="h-[calc(100vh-200px)]">
          <div className="space-y-4 p-4">
            <nav className="space-y-2">
              <Button
                variant={pathname === "/queries" ? "secondary" : "ghost"}
                className={cn("w-full", collapsed ? "justify-center px-0" : "justify-start")}
                asChild
              >
                <Link href="/queries" title="Consultas">
                  <Eye className={cn("h-4 w-4", collapsed ? "mr-0" : "mr-2")} />
                  {!collapsed && <span>Consultas</span>}
                </Link>
              </Button>
              <Button
                variant={pathname === "/databases" ? "secondary" : "ghost"}
                className={cn("w-full", collapsed ? "justify-center px-0" : "justify-start")}
                asChild
              >
                <Link href="/databases" title="Bancos de Dados">
                  <Database className={cn("h-4 w-4", collapsed ? "mr-0" : "mr-2")} />
                  {!collapsed && <span>Bancos de Dados</span>}
                </Link>
              </Button>
              <Button
                variant={pathname === "/templates" ? "secondary" : "ghost"}
                className={cn("w-full", collapsed ? "justify-center px-0" : "justify-start")}
                asChild
              >
                <Link href="/templates" title="Templates">
                  <Layers className={cn("h-4 w-4", collapsed ? "mr-0" : "mr-2")} />
                  {!collapsed && <span>Templates</span>}
                </Link>
              </Button>
            </nav>
          </div>
        </ScrollArea>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        <div className="flex-1 flex flex-col">
          {/* Header */}
          <header className="border-b px-4 flex items-center justify-between bg-muted/10 h-14">
            <h1 className="text-sm font-medium">
              {pathname === "/queries" && "Histórico de Consultas"}
              {pathname.startsWith("/queries/") && "Detalhes da Consulta"}
              {pathname === "/databases" && "Bancos de Dados"}
              {pathname === "/templates" && "Templates"}
            </h1>
            {user && (
              <div className="flex items-center gap-4">
                <div className="flex flex-col items-end">
                  <span className="text-sm font-medium">{user.name}</span>
                  <span className="text-xs text-muted-foreground">{user.email}</span>
                </div>
                <Button variant="ghost" size="icon" onClick={handleLogout} title="Sair">
                  <LogOut className="h-4 w-4" />
                </Button>
              </div>
            )}
          </header>
          {children}
        </div>
      </div>
    </div>
  )
}
