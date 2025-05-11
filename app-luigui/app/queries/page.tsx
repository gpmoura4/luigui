"use client"

import { useState } from "react"
import { Card, CardContent, CardFooter } from "@/components/ui/card"
import { Database, Clock, ArrowRight } from "lucide-react"
import Link from "next/link"
import { Button } from "@/components/ui/button"

// Dados de exemplo para demonstração
const sampleDatabases = [
  {
    id: "db1",
    name: "Vendas",
    connectionType: "direct" as const,
    lastQuery: "2 horas atrás",
    queryCount: 24,
  },
  {
    id: "db2",
    name: "Recursos Humanos",
    connectionType: "direct" as const,
    lastQuery: "1 dia atrás",
    queryCount: 15,
  },
  {
    id: "db3",
    name: "Inventário",
    connectionType: "schema" as const,
    lastQuery: "3 dias atrás",
    queryCount: 8,
  },
  {
    id: "db4",
    name: "Financeiro",
    connectionType: "schema" as const,
    lastQuery: "1 semana atrás",
    queryCount: 12,
  },
]

// Dados de exemplo para consultas
const sampleQueries = [
  {
    id: "q1",
    databaseId: "db1",
    question: "Quais são os 10 clientes com maior valor de compra desde janeiro de 2023?",
    timestamp: "2023-08-15T14:30:00",
    formattedDate: "15/08/2023 14:30",
  },
  {
    id: "q2",
    databaseId: "db1",
    question: "Qual é o produto mais vendido por região?",
    timestamp: "2023-08-14T10:15:00",
    formattedDate: "14/08/2023 10:15",
  },
  {
    id: "q3",
    databaseId: "db1",
    question: "Qual é o total de vendas por mês em 2023?",
    timestamp: "2023-08-12T16:45:00",
    formattedDate: "12/08/2023 16:45",
  },
  {
    id: "q4",
    databaseId: "db2",
    question: "Quais funcionários têm mais de 5 anos de empresa?",
    timestamp: "2023-08-10T09:20:00",
    formattedDate: "10/08/2023 09:20",
  },
  {
    id: "q5",
    databaseId: "db2",
    question: "Qual é a média salarial por departamento?",
    timestamp: "2023-08-08T11:30:00",
    formattedDate: "08/08/2023 11:30",
  },
]

export default function QueriesPage() {
  const [selectedDatabase, setSelectedDatabase] = useState<string | null>(null)

  // Filtrar consultas pelo banco de dados selecionado
  const filteredQueries = selectedDatabase ? sampleQueries.filter((query) => query.databaseId === selectedDatabase) : []

  // Encontrar o banco de dados selecionado
  const selectedDatabaseInfo = sampleDatabases.find((db) => db.id === selectedDatabase)

  return (
    <div className="flex-1 flex flex-col p-6 overflow-y-auto">
      <div className="w-full max-w-6xl mx-auto">
        {/* Cabeçalho com título */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold mb-2">Histórico de Consultas</h1>
          <p className="text-muted-foreground">Visualize e gerencie suas consultas anteriores por banco de dados.</p>
        </div>

        <div className="flex flex-col md:flex-row gap-6">
          {/* Painel esquerdo - Lista de bancos de dados */}
          <div className="w-full md:w-1/3">
            <h2 className="text-lg font-medium mb-4">Bancos de Dados</h2>
            <div className="space-y-3">
              {sampleDatabases.map((db) => (
                <Card
                  key={db.id}
                  className={cn(
                    "cursor-pointer transition-all hover:shadow-md",
                    selectedDatabase === db.id && "border-primary bg-primary/5",
                  )}
                  onClick={() => setSelectedDatabase(db.id)}
                >
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                        <Database className="h-5 w-5 text-primary" />
                      </div>
                      <div>
                        <h3 className="font-medium">{db.name}</h3>
                        <div className="flex items-center gap-1 text-xs text-muted-foreground mt-1">
                          <Clock className="h-3 w-3" />
                          <span>Última consulta: {db.lastQuery}</span>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                  <CardFooter className="bg-muted/20 px-4 py-2 text-xs text-muted-foreground">
                    {db.queryCount} consultas realizadas
                  </CardFooter>
                </Card>
              ))}
            </div>
          </div>

          {/* Painel direito - Lista de consultas ou mensagem de seleção */}
          <div className="w-full md:w-2/3">
            {selectedDatabase ? (
              <>
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-medium">Consultas em {selectedDatabaseInfo?.name}</h2>
                  <Button asChild variant="outline" size="sm" className="gap-1">
                    <Link href="/">
                      <ArrowRight className="h-4 w-4" />
                      Nova Consulta
                    </Link>
                  </Button>
                </div>

                {filteredQueries.length > 0 ? (
                  <div className="space-y-3">
                    {filteredQueries.map((query) => (
                      <Link href={`/queries/${query.id}`} key={query.id}>
                        <Card className="cursor-pointer transition-all hover:shadow-md hover:border-primary">
                          <CardContent className="p-4">
                            <div className="flex flex-col">
                              <p className="font-medium line-clamp-2">{query.question}</p>
                              <div className="flex items-center gap-1 text-xs text-muted-foreground mt-2">
                                <Clock className="h-3 w-3" />
                                <span>{query.formattedDate}</span>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      </Link>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12 bg-muted/20 rounded-lg">
                    <Clock className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                    <h3 className="text-lg font-medium mb-2">Nenhuma consulta encontrada</h3>
                    <p className="text-muted-foreground mb-4">
                      Você ainda não realizou consultas neste banco de dados.
                    </p>
                    <Button asChild className="gap-2">
                      <Link href="/">
                        <ArrowRight className="h-4 w-4" />
                        Nova Consulta
                      </Link>
                    </Button>
                  </div>
                )}
              </>
            ) : (
              <div className="text-center py-12 bg-muted/20 rounded-lg">
                <Database className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium mb-2">Selecione um banco de dados</h3>
                <p className="text-muted-foreground">Escolha um banco de dados à esquerda para ver suas consultas.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

// Função auxiliar para concatenar classes condicionalmente
function cn(...classes: (string | boolean | undefined)[]) {
  return classes.filter(Boolean).join(" ")
}
