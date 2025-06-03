"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { ArrowLeft, Users, Save, Search } from "lucide-react"
import Link from "next/link"
import { ProtectedRoute } from "@/components/protected-route"
import { API_BASE_URL } from "@/config/constants"
import { useAuth } from "@/contexts/AuthContext"
import { Checkbox } from "@/components/ui/checkbox"
import { toast } from "sonner"
import { Input } from "@/components/ui/input"

interface User {
  id: string
  name: string
  email: string
  role: string
  hasAccess?: boolean
  databases?: number[]
}

export default function DatabaseUsersPage() {
  const [users, setUsers] = useState<User[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [searchQuery, setSearchQuery] = useState("")
  const params = useParams()
  const router = useRouter()
  const { user } = useAuth()
  const databaseId = params.id as string

  // Busca todos os usuários e os usuários com acesso ao database
  const fetchUsers = async () => {
    try {
      console.log(`API BASE URL:${API_BASE_URL}`)
      
      const [allUsersResponse] = await Promise.all([
        fetch(`${API_BASE_URL}/api/users/list/`, {
          credentials: "include",
        }),
      ])

      if (!allUsersResponse.ok) 
        throw new Error("Failed to fetch users")

      console.log("allUsersResponse:", allUsersResponse)
      const allUsers = await allUsersResponse.json()

      const employeeUsers = allUsers
        .filter((user: User) => user.role === "employee")
        .map((user: User) => ({
          ...user,
          hasAccess: user.databases?.includes(Number(databaseId)) || false
        }))

      setUsers(employeeUsers)
    } catch (error) {
      console.error("Error fetching users:", error)
      toast.error("Erro ao carregar usuários")
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchUsers()
  }, [databaseId])

  const handleToggleAccess = (userId: string) => {
    setUsers(users.map(user => 
      user.id === userId 
        ? { ...user, hasAccess: !user.hasAccess }
        : user
    ))
  }

  function getCookie(name: string): string {
    const value = `; ${document.cookie}`
    const parts = value.split(`; ${name}=`)
    if (parts.length === 2) return parts.pop()?.split(';').shift() || ''
    return ''
  } 

  const handleSaveAccess = async () => {
    try {
      setIsSaving(true)
      // Separa os usuários em dois grupos: com e sem acesso
      const selectedUserIds = users
        .filter(user => user.hasAccess)
        .map(user => user.id)
      
      const deselectedUserIds = users
        .filter(user => !user.hasAccess)
        .map(user => user.id)

      console.log("selectedUserIds:", selectedUserIds)
      console.log("deselectedUserIds:", deselectedUserIds)

      // Adiciona acesso para usuários selecionados
      if (selectedUserIds.length > 0) {
        const grantResponse = await fetch(`${API_BASE_URL}/api/databases/${databaseId}/access/`, {
          method: 'POST',
          headers: {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
          },
          credentials: "include",
          body: JSON.stringify({ user_ids: selectedUserIds }),
        })

        if (!grantResponse.ok) throw new Error("Failed to grant users access")
      }

      // Remove acesso para usuários desmarcados
      if (deselectedUserIds.length > 0) {
        const removeResponse = await fetch(`${API_BASE_URL}/api/databases/${databaseId}/access/`, {
          method: 'DELETE',
          headers: {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
          },
          credentials: "include",
          body: JSON.stringify({ user_ids: deselectedUserIds }),
        })

        if (!removeResponse.ok) throw new Error("Failed to remove users access")
      }
      
      toast.success("Acesso dos usuários atualizado com sucesso")
      router.refresh()
    } catch (error) {
      console.error("Error updating users access:", error)
      toast.error("Erro ao atualizar acesso dos usuários")
    } finally {
      setIsSaving(false)
    }
  }

  if (user?.role !== "admin") {
    return <div>Acesso não autorizado</div>
  }

  if (isLoading) {
    return <div>Carregando...</div>
  }

  // Filtra os usuários com base na busca
  const filteredUsers = users.filter(user => 
    user.email.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <ProtectedRoute>        
      <div className="flex-1 flex flex-col p-6 overflow-y-auto">
        <div className="w-full max-w-6xl mx-auto">
          {/* Cabeçalho com título e botões */}
          <div className="flex items-center gap-4 mb-8">
            <Link href="/databases">
              <Button variant="ghost" size="icon">
                <ArrowLeft className="h-5 w-5" />
              </Button>
            </Link>
            <div className="flex-1">
              <h1 className="text-2xl font-bold mb-2">Usuários do Banco de Dados</h1>
              <p className="text-muted-foreground">
                Gerencie os usuários que têm acesso a este banco de dados.
              </p>
            </div>
            <Button 
              onClick={handleSaveAccess} 
              disabled={isSaving}
              className="gap-2"
            >
              <Save className="h-4 w-4" />
              {isSaving ? "Salvando..." : "Salvar Alterações"}
            </Button>
          </div>

          {/* Campo de busca */}
          <div className="mb-6">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Buscar usuário por email..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
    
          {/* Lista de usuários */}
          <div className="grid gap-4">
            {filteredUsers.length === 0 ? (
              <div className="text-center py-12">
                <Users className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium mb-2">
                  {searchQuery 
                    ? "Nenhum usuário encontrado para sua busca" 
                    : "Nenhum usuário encontrado"}
                </h3>
                <p className="text-muted-foreground">
                  {searchQuery 
                    ? "Tente buscar com outros termos" 
                    : "Não há usuários do tipo \"employee\" cadastrados no sistema."}
                </p>
              </div>
            ) : (
              filteredUsers.map((user) => (
                <Card key={user.id} className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <Checkbox
                        id={`access-${user.id}`}
                        checked={user.hasAccess}
                        onCheckedChange={() => handleToggleAccess(user.id)}
                      />
                      <div>
                        <h3 className="font-medium">{user.name}</h3>
                        <p className="text-sm text-muted-foreground">
                          ID: {user.id} • {user.email}
                        </p>
                      </div>
                    </div>
                  </div>
                </Card>
              ))
            )}
          </div>
        </div>
      </div>
    </ProtectedRoute>
  )
} 