"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Users, Layers, Eye, X, Database, ChevronLeft, ChevronRight, Plus } from "lucide-react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"

export default function ClientLayout({ children }: { children: React.ReactNode }) {
  const [collapsed, setCollapsed] = useState(false)
  const pathname = usePathname()

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

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <div
        className={cn(
          "border-r bg-muted/10 transition-all duration-300 ease-in-out relative",
          collapsed ? "w-16" : "w-64",
        )}
      >
        <div className="p-4 border-b flex items-center justify-between">
          <div className={cn("flex items-center gap-2", collapsed && "justify-center")}>
            <div className="h-6 w-6 rounded-full bg-primary flex-shrink-0" />
            {!collapsed && <span className="font-semibold">Text-To-SQL</span>}
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

        <ScrollArea className="h-[calc(100vh-128px)]">
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
            <div className="pt-4 border-t">
              <Button variant="ghost" className={cn("w-full", collapsed ? "justify-center px-0" : "justify-start")}>
                <Users className={cn("h-4 w-4", collapsed ? "mr-0" : "mr-2")} />
                {!collapsed && <span>Usuário</span>}
              </Button>
            </div>
          </div>
        </ScrollArea>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        <div className="flex-1 flex flex-col">
          {/* Header */}
          <header className="h-14 border-b px-4 flex items-center justify-between">
            <h1 className="text-sm font-medium">
              {pathname === "/" && "Nova Consulta"}
              {pathname === "/queries" && "Histórico de Consultas"}
              {pathname.startsWith("/queries/") && "Detalhes da Consulta"}
              {pathname === "/databases" && "Bancos de Dados"}
              {pathname === "/templates" && "Templates"}
            </h1>
            <div className="flex items-center gap-2">
            </div>
          </header>
          {children}
        </div>
      </div>
    </div>
  )
}
