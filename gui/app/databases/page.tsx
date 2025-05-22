"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter } from "@/components/ui/card"
import { Database, Edit, Plus, FileCode } from "lucide-react"
import Link from "next/link"
import { DatabaseFormDialog } from "@/components/database-form-dialog"
import { ProtectedRoute } from "@/components/protected-route"

// Dados de exemplo para demonstração
const sampleDatabases = [
  {
    id: "db1",
    name: "Vendas",
    connectionType: "direct" as const,
    connectionDetails: {
      host: "localhost",
      port: "5432",
      username: "postgres",
      password: "****",
      databaseName: "vendas",
    },
  },
  {
    id: "db2",
    name: "Recursos Humanos",
    connectionType: "direct" as const,
    connectionDetails: {
      host: "db.example.com",
      port: "5432",
      username: "admin",
      password: "****",
      databaseName: "rh",
    },
  },
  {
    id: "db3",
    name: "Inventário",
    connectionType: "schema" as const,
    schema: "{ ... schema data ... }",
  },
  {
    id: "db4",
    name: "Financeiro",
    connectionType: "schema" as const,
    schema: "{ ... schema data ... }",
  },
]

export default function DatabasesPage() {
  const [databases, setDatabases] = useState(sampleDatabases)
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [selectedDatabase, setSelectedDatabase] = useState<(typeof sampleDatabases)[0] | undefined>(undefined)

  const handleNewDatabase = () => {
    setSelectedDatabase(undefined)
    setIsDialogOpen(true)
  }

  const handleEditDatabase = (database: (typeof sampleDatabases)[0]) => {
    setSelectedDatabase(database)
    setIsDialogOpen(true)
  }

  return (
    <ProtectedRoute>
      <div className="flex-1 flex flex-col p-6 overflow-y-auto">
        <div className="w-full max-w-6xl mx-auto">
          {/* Cabeçalho com título */}
          <div className="mb-8">
            <h1 className="text-2xl font-bold mb-2">Bancos de Dados</h1>
            <p className="text-muted-foreground">
              Gerencie suas conexões de banco de dados para consultas em linguagem natural.
            </p>
          </div>

          {/* Seção de call-to-action e botão New Database */}
          <div className="bg-muted/30 rounded-lg p-6 mb-8 flex flex-col sm:flex-row justify-between items-center gap-4">
            <div>
              <h2 className="text-lg font-medium mb-1">Registre um novo banco de dados</h2>
              <p className="text-muted-foreground max-w-xl">
                Conecte seu banco de dados para começar a fazer consultas em linguagem natural. Suportamos PostgreSQL,
                MySQL, SQL Server e outros.
              </p>
            </div>
            <Button className="gap-2 whitespace-nowrap" size="lg" onClick={handleNewDatabase}>
              <Plus className="h-4 w-4" />
              Novo Banco de Dados
            </Button>
          </div>

          {/* Grid de cards de bancos de dados */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {databases.map((db) => (
              <DatabaseCard key={db.id} database={db} onEdit={() => handleEditDatabase(db)} />
            ))}
          </div>

          {/* Mensagem para quando não há bancos de dados */}
          {databases.length === 0 && (
            <div className="text-center py-12">
              <Database className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-medium mb-2">Nenhum banco de dados registrado</h3>
              <p className="text-muted-foreground mb-4">
                Registre seu primeiro banco de dados para começar a fazer consultas.
              </p>
              <Button className="gap-2" onClick={handleNewDatabase}>
                <Plus className="h-4 w-4" />
                Novo Banco de Dados
              </Button>
            </div>
          )}
        </div>

        {/* Modal de formulário */}
        <DatabaseFormDialog open={isDialogOpen} onOpenChange={setIsDialogOpen} database={selectedDatabase} />
      </div>
    </ProtectedRoute>
  )
}

// Componente de card para banco de dados
function DatabaseCard({
  database,
  onEdit,
}: {
  database: {
    id: string
    name: string
    connectionType: "direct" | "schema"
    connectionDetails?: {
      host: string
      port: string
      username: string
      password: string
      databaseName: string
    }
    schema?: string
  }
  onEdit: () => void
}) {
  return (
    <Card className="overflow-hidden transition-all hover:shadow-md">
      <CardContent className="p-0">
        <div className="p-6">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                {database.connectionType === "direct" ? (
                  <Database className="h-5 w-5 text-primary" />
                ) : (
                  <FileCode className="h-5 w-5 text-primary" />
                )}
              </div>
              <div>
                <h3 className="font-medium">{database.name}</h3>
                <p className="text-xs text-muted-foreground mt-1">
                  {database.connectionType === "direct" ? "Conexão Direta" : "Esquema Fornecido"}
                </p>
              </div>
            </div>
            <Button variant="ghost" size="icon" className="h-8 w-8" title="Editar banco de dados" onClick={onEdit}>
              <Edit className="h-4 w-4" />
            </Button>
          </div>
          {database.connectionType === "direct" && database.connectionDetails && (
            <p className="text-xs text-muted-foreground mt-4 font-mono truncate">
              {`${database.connectionDetails.username}@${database.connectionDetails.host}:${database.connectionDetails.port}/${database.connectionDetails.databaseName}`}
            </p>
          )}
          {database.connectionType === "schema" && (
            <p className="text-xs text-muted-foreground mt-4">Esquema fornecido manualmente</p>
          )}
        </div>
      </CardContent>
      <CardFooter className="bg-muted/20 px-6 py-3 flex justify-between">
        <span className="text-xs text-muted-foreground">Última consulta: há 2 horas</span>
        <Link href={`/?db=${database.id}`} className="text-xs text-primary hover:underline">
          Fazer consulta
        </Link>
      </CardFooter>
    </Card>
  )
}
