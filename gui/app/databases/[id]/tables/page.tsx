"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { ArrowLeft, Database, Table as TableIcon, Search, Trash2, Plus } from "lucide-react"
import Link from "next/link"
import { ProtectedRoute } from "@/components/protected-route"
import { API_BASE_URL } from "@/config/constants"
import { Input } from "@/components/ui/input"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { toast } from "sonner"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { useAuth } from "@/contexts/AuthContext"

interface TableType {
  id: string
  name: string
  database: string
}

interface DatabaseType {
  id: string
  name: string
  type: "complete" | "minimal"
}

export default function DatabaseTablesPage() {
  const params = useParams()
  const [tables, setTables] = useState<TableType[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")
  const [tableToDelete, setTableToDelete] = useState<TableType | null>(null)
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [database, setDatabase] = useState<DatabaseType | null>(null)
  const [formData, setFormData] = useState({
    name: "",
    db_password: "",
    schemas: ""
  })
  const { user } = useAuth()
  const isAdmin = user?.role === 'admin'

  const fetchDatabase = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/databases/${params.id}`, {
        credentials: "include",
      })
      if (!response.ok) throw new Error("Failed to fetch database")
      const data = await response.json()
      setDatabase(data)
    } catch (error) {
      console.error("Error fetching database:", error)
      toast.error("Erro ao carregar informações do banco de dados")
    }
  }

  const fetchTables = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/databases/${params.id}/tables/`, {
        credentials: "include",
      })
      if (!response.ok) throw new Error("Failed to fetch tables")
      const data = await response.json()
      setTables(data)
    } catch (error) {
      console.error("Error fetching tables:", error)
    } finally {
      setIsLoading(false)
    }
  }
  
  function getCookie(name: string): string {
    const value = `; ${document.cookie}`
    const parts = value.split(`; ${name}=`)
    if (parts.length === 2) return parts.pop()?.split(';').shift() || ''
    return ''
  } 

  const handleCreateTable = async (e: React.FormEvent) => {
    e.preventDefault()
    
    try {
      const payload = database?.type === "complete" 
        ? { name: formData.name, db_password: formData.db_password }
        : { schemas: formData.schemas }

      const response = await fetch(`${API_BASE_URL}/api/databases/${params.id}/tables/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
          },
        credentials: "include",
        body: JSON.stringify(payload),
      })

      if (!response.ok) throw new Error("Failed to create table")

      toast.success("Tabela criada com sucesso")
      setIsCreateDialogOpen(false)
      setFormData({ name: "", db_password: "", schemas: "" })
      fetchTables()
    } catch (error) {
      console.error("Error creating table:", error)
      toast.error("Erro ao criar tabela")
    }
  }

  const handleDeleteTable = async () => {
    if (!tableToDelete) return

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/databases/${params.id}/tables/${tableToDelete.id}/`,
        {
          method: "DELETE",
          credentials: "include",
        }
      )

      if (!response.ok) throw new Error("Failed to delete table")

      toast.success("Tabela excluída com sucesso")
      setTableToDelete(null)
      fetchTables()
    } catch (error) {
      console.error("Error deleting table:", error)
      toast.error("Erro ao excluir tabela")
    }
  }

  useEffect(() => {
    fetchDatabase()
    fetchTables()
  }, [params.id])

  // Filtra as tabelas baseado na busca
  const filteredTables = tables.filter(table =>
    table.name.toLowerCase().includes(searchQuery.toLowerCase())
  )

  if (isLoading) {
    return <div>Carregando...</div>
  }

  return (
    <ProtectedRoute>
      <div className="flex-1 flex flex-col p-6 overflow-y-auto">
        <div className="w-full max-w-6xl mx-auto">
          {/* Cabeçalho com botão de voltar */}
          <div className="flex items-center gap-4 mb-8">
            <Button variant="ghost" size="icon" asChild>
              <Link href="/databases">
                <ArrowLeft className="h-4 w-4" />
              </Link>
            </Button>
            <div>
              <h1 className="text-2xl font-bold mb-2">Tabelas do Banco de Dados</h1>
              <p className="text-muted-foreground">
                Visualize e gerencie as tabelas disponíveis neste banco de dados.
              </p>
            </div>
          </div>

          {/* Seção de busca e botão de criar */}
          <div className="bg-muted/30 rounded-lg p-6 mb-8">
            <div className="flex flex-col sm:flex-row justify-between items-stretch sm:items-center gap-4">
              <div className="flex-1">
                <h2 className="text-lg font-medium mb-1">Tabelas Disponíveis</h2>
                <p className="text-muted-foreground max-w-xl">
                  Veja todas as tabelas disponíveis neste banco de dados e suas informações.
                </p>
              </div>
              {isAdmin && (
                <Button 
                  className="gap-2 whitespace-nowrap" 
                  size="lg" 
                  onClick={() => setIsCreateDialogOpen(true)}
                >
                  <Plus className="h-4 w-4" />
                  Nova Tabela
                </Button>
              )}
            </div>
            
            {/* Campo de busca */}
            <div className="mt-4 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Buscar tabela por nome..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>

          {/* Lista de tabelas */}
          {filteredTables.length > 0 ? (
            <Card className="overflow-hidden">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-12"></TableHead>
                    <TableHead>Nome da Tabela</TableHead>
                    <TableHead className="text-right">Ações</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredTables.map((table) => (
                    <TableRow key={table.id}>
                      <TableCell>
                        <TableIcon className="h-4 w-4 text-muted-foreground" />
                      </TableCell>
                      <TableCell className="font-medium">{table.name}</TableCell>
                      <TableCell className="text-right space-x-2">
                        {isAdmin && (
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-destructive hover:text-destructive hover:bg-destructive/10"
                            onClick={() => setTableToDelete(table)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Card>
          ) : (
            <div className="text-center py-12">
              <Database className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-medium mb-2">
                {searchQuery
                  ? "Nenhuma tabela encontrada para sua busca"
                  : "Nenhuma tabela registrada"}
              </h3>
              <p className="text-muted-foreground mb-4">
                {searchQuery
                  ? "Tente buscar com outros termos"
                  : "Este banco de dados ainda não possui tabelas registradas."}
              </p>
              {!searchQuery && isAdmin && (
                <Button className="gap-2" onClick={() => setIsCreateDialogOpen(true)}>
                  <Plus className="h-4 w-4" />
                  Nova Tabela
                </Button>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Diálogo de criação de tabela */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Criar Nova Tabela</DialogTitle>
            <DialogDescription>
              {database?.type === "complete"
                ? "Informe o nome da tabela e a senha do banco de dados."
                : "Informe os schemas da tabela em formato SQL."}
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleCreateTable}>
            <div className="space-y-4 py-4">
              {database?.type === "complete" ? (
                <>
                  <div className="space-y-2">
                    <Label htmlFor="name">Nome da Tabela</Label>
                    <Input
                      id="name"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      placeholder="Digite o nome da tabela"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="password">Senha do Banco de Dados</Label>
                    <Input
                      id="password"
                      type="password"
                      value={formData.db_password}
                      onChange={(e) => setFormData({ ...formData, db_password: e.target.value })}
                      placeholder="Digite a senha do banco de dados"
                      required
                    />
                  </div>
                </>
              ) : (
                <div className="space-y-2">
                  <Label htmlFor="schemas">Schemas da Tabela</Label>
                  <Textarea
                    id="schemas"
                    value={formData.schemas}
                    onChange={(e) => setFormData({ ...formData, schemas: e.target.value })}
                    placeholder="Digite os schemas da tabela em formato SQL"
                    className="h-32"
                    required
                  />
                </div>
              )}
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                Cancelar
              </Button>
              <Button type="submit">Criar Tabela</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Diálogo de confirmação de exclusão */}
      <AlertDialog open={!!tableToDelete} onOpenChange={() => setTableToDelete(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Confirmar exclusão</AlertDialogTitle>
            <AlertDialogDescription>
              Tem certeza que deseja excluir a tabela "{tableToDelete?.name}"?
              Esta ação não pode ser desfeita.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancelar</AlertDialogCancel>
            <AlertDialogAction
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              onClick={handleDeleteTable}
            >
              Excluir
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </ProtectedRoute>
  )
} 