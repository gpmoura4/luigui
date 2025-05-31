"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter } from "@/components/ui/card"
import { Database, Edit, Plus, FileCode, Search, Users } from "lucide-react"
import Link from "next/link"
import { DatabaseFormDialog } from "@/components/database-form-dialog"
import { ProtectedRoute } from "@/components/protected-route"
import { API_BASE_URL } from "@/config/constants"
import { Input } from "@/components/ui/input"
import { useAuth } from "@/contexts/AuthContext"

interface DatabaseType {
  id: string
  name: string
  type: "complete" | "minimal"
  host?: string
  port?: string
  username?: string
  db_name?: string
}

export default function DatabasesPage() {
  const [databases, setDatabases] = useState<DatabaseType[]>([])
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [selectedDatabase, setSelectedDatabase] = useState<DatabaseType | undefined>(undefined)
  const [isLoading, setIsLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")
  const { user } = useAuth()

  const fetchDatabases = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/databases/`, {
        credentials: "include",
      })
      if (!response.ok) throw new Error("Failed to fetch databases")
      const data = await response.json()
      setDatabases(data)
    } catch (error) {
      console.error("Error fetching databases:", error)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchDatabases()
  }, [])

  const handleNewDatabase = () => {
    setSelectedDatabase(undefined)
    setIsDialogOpen(true)
  }

  const handleEditDatabase = (database: DatabaseType) => {
    setSelectedDatabase(database)
    setIsDialogOpen(true)
  }

  const handleDatabaseChange = () => {
    fetchDatabases()
  }

  // Filtra os databases baseado na busca
  const filteredDatabases = databases.filter(db =>
    db.name.toLowerCase().includes(searchQuery.toLowerCase())
  )

  if (isLoading) {
    return <div>Carregando...</div>
  }

  const isAdmin = user?.role === 'admin'
  console.log("user TODO:",user)
  console.log("user role:",user?.role)

  return (
    <ProtectedRoute>
      <div className="flex-1 flex flex-col p-6 overflow-y-auto">
        <div className="w-full max-w-6xl mx-auto">
          {/* Cabeçalho com título */}
          <div className="mb-8">
            <h1 className="text-2xl font-bold mb-2">Bancos de Dados</h1>
            <p className="text-muted-foreground">
              {isAdmin 
                ? "Gerencie suas conexões de banco de dados para consultas em linguagem natural."
                : "Visualize e acesse os bancos de dados disponíveis para consultas em linguagem natural."}
            </p>
          </div>

          {/* Seção de busca e botão New Database */}
          <div className="bg-muted/30 rounded-lg p-6 mb-8">
            <div className="flex flex-col sm:flex-row justify-between items-stretch sm:items-center gap-4">
              <div className="flex-1">
                <h2 className="text-lg font-medium mb-1">
                  {isAdmin 
                    ? "Registre um novo banco de dados"
                    : "Acesse os bancos de dados disponíveis"}
                </h2>
                <p className="text-muted-foreground max-w-xl">
                  {isAdmin 
                    ? "Conecte seu banco de dados para começar a fazer consultas em linguagem natural. Suportamos PostgreSQL, MySQL, SQL Server e outros."
                    : "Selecione um banco de dados para começar a fazer consultas em linguagem natural."}
                </p>
              </div>
              {isAdmin && (
                <Button className="gap-2 whitespace-nowrap" size="lg" onClick={handleNewDatabase}>
                  <Plus className="h-4 w-4" />
                  Novo Banco de Dados
                </Button>
              )}
            </div>
            
            {/* Campo de busca */}
            <div className="mt-4 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Buscar banco de dados por nome..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>

          {/* Grid de cards de bancos de dados */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredDatabases.map((db) => (
              <DatabaseCard 
                key={db.id} 
                database={db} 
                onEdit={() => handleEditDatabase(db)}
                isAdmin={isAdmin}
              />
            ))}
          </div>

          {/* Mensagem para quando não há bancos de dados */}
          {filteredDatabases.length === 0 && (
            <div className="text-center py-12">
              <Database className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-medium mb-2">
                {searchQuery
                  ? "Nenhum banco de dados encontrado para sua busca"
                  : "Nenhum banco de dados registrado"}
              </h3>
              <p className="text-muted-foreground mb-4">
                {searchQuery
                  ? "Tente buscar com outros termos"
                  : isAdmin 
                    ? "Registre seu primeiro banco de dados para começar a fazer consultas."
                    : "Aguarde até que um administrador registre um banco de dados."}
              </p>
              {!searchQuery && isAdmin && (
                <Button className="gap-2" onClick={handleNewDatabase}>
                  <Plus className="h-4 w-4" />
                  Novo Banco de Dados
                </Button>
              )}
            </div>
          )}
        </div>

        {/* Modal de formulário */}
        <DatabaseFormDialog 
          open={isDialogOpen} 
          onOpenChange={setIsDialogOpen} 
          database={selectedDatabase}
          onDatabaseChange={handleDatabaseChange}
        />
      </div>
    </ProtectedRoute>
  )
}

// Componente de card para banco de dados
function DatabaseCard({
  database,
  onEdit,
  isAdmin,
}: {
  database: DatabaseType
  onEdit: () => void
  isAdmin: boolean
}) {
  return (
    <Card className="overflow-hidden transition-all hover:shadow-md flex flex-col">
      <CardContent className="p-0 flex-1">
        <div className="p-6">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
                {database.type === "complete" ? (
                  <Database className="h-6 w-6 text-primary" />
                ) : (
                  <FileCode className="h-6 w-6 text-primary" />
                )}
              </div>
              <div>
                <h3 className="text-lg font-medium">{database.name}</h3>
                <p className="text-sm text-muted-foreground mt-1">
                  {database.type === "complete" ? "Conexão Direta" : "Esquema Fornecido"}
                </p>
              </div>
            </div>
            {isAdmin && (
              <Button 
                variant="ghost" 
                size="icon" 
                className="h-8 w-8 hover:bg-primary/10" 
                title="Editar banco de dados" 
                onClick={onEdit}
              >
                <Edit className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
      </CardContent>
      <CardFooter className="bg-muted/10 px-6 py-4 flex justify-center items-center gap-4 border-t">
        {isAdmin && (
          <Button 
            variant="outline"
            size="sm"
            className="gap-2 hover:bg-primary/10 min-w-[160px] justify-center"
            asChild
          >
            <Link href={`/databases/${database.id}/users`}>
              <Users className="h-4 w-4" />
              Gerenciar Usuários
            </Link>
          </Button>
        )}
        <Button 
          variant="default"
          size="sm"
          className="gap-2 min-w-[160px] justify-center"
          asChild
        >
          <Link href={`/?db=${database.id}`}>
            <Search className="h-4 w-4" />
            Fazer Consulta
          </Link>
        </Button>
      </CardFooter>
    </Card>
  )
}

