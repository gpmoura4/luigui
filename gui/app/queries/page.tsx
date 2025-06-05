"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardFooter } from "@/components/ui/card"
import { Database, Clock, ArrowRight } from "lucide-react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { API_BASE_URL } from "@/config/constants"
import { toast } from "sonner"

interface Database {
  id: string
  name: string
  type: string
  connection_type: string
}

interface Question {
  id: string
  database: number
  question: string
  answer: string
  query: string
  prompt_type: string
}

// Função para formatar o tipo do banco de dados
function formatDatabaseType(type: string): string {
  switch (type) {
    case "complete":
      return "Conexão Direta"
    case "minimal":
      return "Esquema Fornecido"
    default:
      return type
  }
}

export default function QueriesPage() {
  const [selectedDatabase, setSelectedDatabase] = useState<string | null>(null)
  const [databases, setDatabases] = useState<Database[]>([])
  const [questions, setQuestions] = useState<Question[]>([])
  const [isLoadingDatabases, setIsLoadingDatabases] = useState(true)
  const [isLoadingQuestions, setIsLoadingQuestions] = useState(false)

  function getCookie(name: string): string {
    const value = `; ${document.cookie}`
    const parts = value.split(`; ${name}=`)
    if (parts.length === 2) return parts.pop()?.split(';').shift() || ''
    return ''
  }

  // Fetch databases
  const fetchDatabases = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/databases/`, {
        credentials: "include",
        headers: {
          "Accept": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
      })

      if (!response.ok) throw new Error("Failed to fetch databases")

      const data = await response.json()
      setDatabases(data)
    } catch (error) {
      console.error("Error fetching databases:", error)
      toast.error("Erro ao carregar bancos de dados")
    } finally {
      setIsLoadingDatabases(false)
    }
  }

  // Fetch questions for selected database
  const fetchQuestions = async (databaseId: string) => {
    try {
      setIsLoadingQuestions(true)
      const response = await fetch(`${API_BASE_URL}/api/databases/${databaseId}/question`, {
        credentials: "include",
        headers: {
          "Accept": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
      })

      if (!response.ok) throw new Error("Failed to fetch questions")

      const data = await response.json()
      setQuestions(data)
    } catch (error) {
      console.error("Error fetching questions:", error)
      toast.error("Erro ao carregar histórico de perguntas")
    } finally {
      setIsLoadingQuestions(false)
    }
  }

  useEffect(() => {
    fetchDatabases()
  }, [])

  useEffect(() => {
    if (selectedDatabase) {
      fetchQuestions(selectedDatabase)
    }
  }, [selectedDatabase])

  // Find the selected database info
  const selectedDatabaseInfo = databases.find((db) => db.id === selectedDatabase)

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
            {isLoadingDatabases ? (
              <div className="text-center py-12">Carregando bancos de dados...</div>
            ) : (
              <div className="space-y-3">
                {databases.map((db) => (
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
                          <p className="text-sm text-muted-foreground">
                            {formatDatabaseType(db.type)}
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
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

                {isLoadingQuestions ? (
                  <div className="text-center py-12">Carregando histórico de consultas...</div>
                ) : questions.length > 0 ? (
                  <div className="space-y-3">
                    {questions.map((query, index) => (
                      <Card key={index} className="cursor-pointer transition-all hover:shadow-md hover:border-primary">
                        <CardContent className="p-4">
                          <div className="space-y-2">
                            <div>
                              <h3 className="font-medium text-primary mb-1">Pergunta:</h3>
                              <p className="text-sm">{query.question}</p>
                            </div>
                            <div>
                              <h3 className="font-medium text-primary mb-1">Resposta:</h3>
                              <p className="text-sm">{query.answer}</p>
                            </div>
                            <div>
                              <h3 className="font-medium text-primary mb-1">Query SQL:</h3>
                              <pre className="text-sm bg-muted p-2 rounded-md overflow-x-auto">
                                {query.query}
                              </pre>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
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
