"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Copy, Database, ChevronDown, ChevronUp, Code, Sparkles, Lock, Search } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator } from "@/components/ui/dropdown-menu"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import Link from "next/link"
import { useSearchParams } from "next/navigation"

// Interface para o tipo Database baseado no serializer do Django
interface Database {
  id: string
  name: string
  type: "complete" | "minimal"
  username?: string
  port?: string
  host?: string
}

// Lista de templates disponíveis
const templates = [
  {
    id: "generate",
    name: "Gerar Consulta SQL",
    prompt: "",
    title: "Faça sua pergunta",
    placeholder: "Exemplo: Quais são os produtos mais vendidos?",
    apiValue: "text_to_sql"
  },
  {
    id: "optimize",
    name: "Otimizar Consulta",
    prompt: "",
    title: "Otimize uma consulta SQL",
    placeholder: "Exemplo: SELECT * FROM produtos p JOIN categorias c ON p.categoria_id = c.id WHERE p.preco > 100;",
    apiValue: "optimize_sql"
  },
  {
    id: "explain",
    name: "Explicar Consulta",
    prompt: "",
    title: "Receba uma explicação detalhada da sua consulta",
    placeholder: "Exemplo: SELECT nome, COUNT(*) as total FROM vendas GROUP BY nome HAVING COUNT(*) > 5;",
    apiValue: "explain_sql"
  },
  {
    id: "correct",
    name: "Corrigir Consulta",
    prompt: "",
    title: "Corrija uma consulta SQL",
    placeholder: "Exemplo: SELECT nome, preco FROM produtos WERE preco > 100 ORDERY BY preco;",
    apiValue: "fix_sql"
  },
]

export default function QuestionAnswerInterface() {
  const searchParams = useSearchParams()
  const [databases, setDatabases] = useState<Database[]>([])
  const [isLoadingDatabases, setIsLoadingDatabases] = useState(true)
  const [question, setQuestion] = useState("")
  const [answer, setAnswer] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [selectedDb, setSelectedDb] = useState<Database | null>(null)
  const [sqlQuery, setSqlQuery] = useState("")
  const [isSqlOpen, setIsSqlOpen] = useState(false)
  const [selectedTemplate, setSelectedTemplate] = useState<(typeof templates)[0]>(templates[0])
  
  // Estados para o modal de senha
  const [isPasswordModalOpen, setIsPasswordModalOpen] = useState(false)
  const [dbPassword, setDbPassword] = useState<string>("")
  const [passwordError, setPasswordError] = useState<string>("")
  const [tempQuestion, setTempQuestion] = useState<string>("")
  const [searchQuery, setSearchQuery] = useState("")

  // Função para buscar os databases da API
  const fetchDatabases = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'}/api/databases/`, {
        credentials: 'include',
      })
      
      if (!response.ok) {
        throw new Error('Failed to fetch databases')
      }

      const data = await response.json()
      setDatabases(data)
      
      // Apenas seleciona um database se houver um ID específico na URL
      const dbId = searchParams.get("db")
      if (dbId) {
        const selectedDatabase = data.find((db: Database) => db.id === dbId)
        if (selectedDatabase) {
          setSelectedDb(selectedDatabase)
        }
      }
    } catch (error) {
      console.error('Error fetching databases:', error)
    } finally {
      setIsLoadingDatabases(false)
    }
  }

  // Carregar databases quando o componente montar
  useEffect(() => {
    fetchDatabases()
  }, [searchParams])

  // Carregar template e pergunta dos parâmetros de URL
  useEffect(() => {
    const templateId = searchParams.get("template")
    const questionParam = searchParams.get("question")

    if (templateId) {
      const template = templates.find((t) => t.id === templateId)
      if (template) {
        setSelectedTemplate(template)
        setQuestion(template.prompt + (questionParam || ""))
      }
    } else if (questionParam) {
      setQuestion(questionParam)
    }
  }, [searchParams])

  // Função para lidar com a seleção de database
  const handleDatabaseSelect = (db: Database) => {
    setSelectedDb(db)
    // Limpa a senha quando troca de database
    setDbPassword("")
  }

  const handleSubmit = async () => {
    if (!question.trim() || !selectedDb) return

    // Se for database complete e não tiver senha, abre o modal
    if (selectedDb.type === "complete" && !dbPassword) {
      setTempQuestion(question) // Guarda a pergunta temporariamente
      setIsPasswordModalOpen(true)
      return
    }

    await submitQuestion()
  }

  // Nova função para submeter a pergunta
  const submitQuestion = async () => {
    setIsLoading(true)
    setSqlQuery("")
    setAnswer("")
    setPasswordError("")

    try {
      // Obter o token CSRF primeiro
      const csrfResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'}/api/csrf/`, {
        method: 'GET',
        credentials: 'include',
      })

      let csrfToken = null
      if (csrfResponse.ok) {
        const cookies = document.cookie.split(';')
        const csrfCookie = cookies.find(cookie => cookie.trim().startsWith('csrftoken='))
        if (csrfCookie) {
          csrfToken = csrfCookie.split('=')[1]
        }
      }

      // Fazer a requisição principal com o token CSRF
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'}/api/databases/${selectedDb!.id}/question`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          ...(csrfToken ? { 'X-CSRFToken': csrfToken } : {}),
        },
        credentials: 'include',
        body: JSON.stringify({
          question: question,
          prompt_type: selectedTemplate.apiValue,
          db_password: selectedDb!.type === "complete" ? dbPassword : undefined
        }),
      })

      let data
      try {
        data = await response.json()
      } catch (e) {
        // Se não conseguir fazer parse do JSON, tenta pegar o texto
        const errorText = await response.text()
        throw new Error(
          `Erro do servidor: ${response.status} - ${
            errorText.length > 100 ? 
            'Erro interno do servidor. Por favor, tente novamente mais tarde.' : 
            errorText
          }`
        )
      }

      if (!response.ok) {
        if (response.status === 403) {
          throw new Error("Erro de autorização. Por favor, verifique se você está logado e tem permissão para acessar este recurso.")
        }

        if (data.ERROR === "db_password password not provided" || (data.ERROR && data.ERROR.includes("password"))) {
          setPasswordError("Senha incorreta ou não fornecida. Por favor, tente novamente.")
          if (selectedDb?.type === "complete") {
            setIsPasswordModalOpen(true)
            return
          }
        }
        console.log("data.ERROR", data.ERROR)
        console.log("data.detail", data.detail)
        console.log("data.natural_language_response", data.natural_language_response)
        
        
        throw new Error(data.ERROR || data.detail || data.natural_language_response || 'Erro ao processar sua pergunta')

      }

      // Validar a estrutura da resposta
      if (!data.natural_language_response && !data.answer && !data.sql_query && !data.query) {
        throw new Error('Resposta inválida do servidor')
      }

      // Para bancos minimal, a resposta pode ser apenas a query SQL
      const sqlQueryText = data.sql_query || data.query || ""
      setSqlQuery(sqlQueryText)
      setIsSqlOpen(true)

      // Se for banco minimal E template text-to-sql, não exibimos a query como resposta em linguagem natural
      if (selectedDb?.type === "minimal" && selectedTemplate.apiValue === "text_to_sql") {
        setAnswer("") // Não exibe resposta em linguagem natural
      } else {
        // Para todos os outros casos, usamos a resposta em linguagem natural se disponível
        const responseText = data.natural_language_response || data.answer || ""
        setAnswer(responseText)
      }
    } catch (error) {
      console.error('Error getting answer:', error)
      if (error instanceof Error) {
        setAnswer(`${error.message}`)
      } else {
        setAnswer("Ocorreu um erro ao processar sua pergunta. Por favor, tente novamente.")
      }
    } finally {
      setIsLoading(false)
    }
  }

  // Handler para o submit do modal de senha
  const handlePasswordSubmit = async () => {
    if (!dbPassword.trim()) {
      setPasswordError("Por favor, insira a senha do banco de dados.")
      return
    }
    setIsPasswordModalOpen(false)
    await submitQuestion()
  }

  // Função para copiar texto para a área de transferência
  const copyToClipboard = (text: string) => {
    navigator.clipboard
      .writeText(text)
      .then(() => {
        console.log("Texto copiado para a área de transferência")
      })
      .catch((err) => {
        console.error("Erro ao copiar texto: ", err)
      })
  }

  // Função para aplicar um template
  const applyTemplate = (template: (typeof templates)[0]) => {
    setSelectedTemplate(template)
    setQuestion(template.prompt)
  }

  // Função para filtrar databases baseado na pesquisa
  const filteredDatabases = databases.filter(db => 
    db.name.toLowerCase().includes(searchQuery.toLowerCase())
  )

  // Componente de lista de databases
  const DatabasesList = ({ onSelect }: { onSelect: (db: Database) => void }) => (
    <>
      <div className="relative">
        <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Pesquisar banco de dados..."
          className="pl-8"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>
      <div className="mt-2">
        {filteredDatabases.length > 0 ? (
          filteredDatabases.map((db) => (
            <DropdownMenuItem key={db.id} onClick={() => onSelect(db)} className="cursor-pointer">
              <div className="flex items-center gap-2">
                {db.name}
                {db.type === "complete" && <Lock className="h-3 w-3 text-muted-foreground" />}
              </div>
            </DropdownMenuItem>
          ))
        ) : (
          <div className="text-center py-2 text-sm text-muted-foreground">
            {databases.length === 0 ? (
              "Nenhum banco cadastrado"
            ) : (
              "Nenhum banco encontrado"
            )}
          </div>
        )}
      </div>
    </>
  )

  return (
    <div className="h-screen flex flex-col items-center p-6 gap-6 overflow-y-auto">
      <div className="w-full max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-primary to-purple-600 bg-clip-text text-transparent">
            Transforme suas perguntas em consultas SQL poderosas
          </h1>
          <div className="flex flex-col items-center text-center gap-1 mt-2">
            <p className="text-xl font-medium text-primary">
              Pergunte em português, receba em SQL
            </p>
            <p className="text-muted-foreground text-sm max-w-2xl">
              Conecte seu banco de dados para ver os resultados em tempo real. 
              Aproveite recursos extras para otimizar, entender e corrigir suas consultas.
            </p>
          </div>
        </div>

        <Card className="shadow-md">
          <CardContent className="pt-6">
            <div className="space-y-4">
              {!selectedDb && (
                <div className="flex flex-col items-center justify-center p-6 text-center border-2 border-dashed rounded-lg border-muted-foreground/20">
                  <Database className="h-8 w-8 text-muted-foreground mb-2" />
                  <h3 className="font-medium text-lg mb-1">Selecione um Banco de Dados</h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    Para começar, escolha um banco de dados para fazer suas consultas
                  </p>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="outline" className="gap-2" disabled={isLoadingDatabases}>
                        <Database className="h-4 w-4" />
                        {isLoadingDatabases ? "Carregando..." : "Selecionar Banco de Dados"}
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="center" className="w-[300px]">
                      <div className="p-2">
                        <DatabasesList onSelect={handleDatabaseSelect} />
                      </div>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem asChild>
                        <Link href="/databases" className="w-full cursor-pointer text-primary">
                          Gerenciar bancos de dados
                        </Link>
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              )}

              {selectedDb && (
                <>
                  <h2 className="text-lg font-medium">{selectedTemplate ? selectedTemplate.title : "Faça sua pergunta"}</h2>
                  <Textarea
                    placeholder={selectedTemplate ? selectedTemplate.placeholder : "Digite sua pergunta aqui..."}
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    className="min-h-[100px] resize-none"
                  />
                  <div className="flex justify-between items-center gap-4">
                    <div className="flex gap-2">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="outline" className="gap-2">
                            <Database className="h-4 w-4" />
                            <div className="flex items-center gap-2">
                              {selectedDb.name}
                              {selectedDb.type === "complete" && <Lock className="h-3 w-3 text-muted-foreground" />}
                            </div>
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="start" side="bottom" className="w-[300px]">
                          <div className="p-2">
                            <DatabasesList onSelect={handleDatabaseSelect} />
                          </div>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem asChild className="cursor-pointer text-primary">
                            <Link href="/databases" className="w-full">
                              Gerenciar bancos de dados
                            </Link>
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>

                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="outline" className="gap-2">
                            <Sparkles className="h-4 w-4" />
                            {selectedTemplate.name}
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end" className="w-56">
                          {templates.map((template) => (
                            <DropdownMenuItem
                              key={template.id}
                              onClick={() => applyTemplate(template)}
                              className="cursor-pointer"
                            >
                              {template.name}
                            </DropdownMenuItem>
                          ))}
                          <DropdownMenuItem asChild className="cursor-pointer text-primary">
                            <Link href="/templates" className="w-full">
                              Ver todos os templates
                            </Link>
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>

                    <Button 
                      onClick={handleSubmit} 
                      disabled={!question.trim() || isLoading} 
                      className="px-8"
                    >
                      {isLoading ? "Processando..." : "Enviar"}
                    </Button>
                  </div>
                </>
              )}
            </div>
          </CardContent>
        </Card>

        {(answer || sqlQuery) && (
          <Card className="mt-6 shadow-md">
            <CardContent className="pt-6">
              <div className="space-y-4">
                {/* Resposta em linguagem natural com ícone de cópia no canto superior direito */}
                {answer && (
                  <div className="relative p-4 bg-muted/50 rounded-lg min-h-[150px]">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="absolute top-2 right-2 h-8 w-8"
                      title="Copiar resposta"
                      onClick={() => copyToClipboard(answer)}
                    >
                      <Copy className="h-4 w-4" />
                    </Button>
                    <p className="text-sm whitespace-pre-wrap pr-10">{answer}</p>
                  </div>
                )}

                {/* SQL Query colapsável */}
                {sqlQuery && (
                  <Collapsible open={isSqlOpen} onOpenChange={setIsSqlOpen} className="border rounded-md">
                    <CollapsibleTrigger asChild>
                      <div className="flex items-center justify-between p-3 cursor-pointer hover:bg-muted/30 border-b border-b-transparent data-[state=open]:border-b-border">
                        <div className="flex items-center gap-2">
                          <Code className="h-4 w-4 text-muted-foreground" />
                          <h3 className="text-sm font-medium">SQL Gerado</h3>
                        </div>
                        <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                          {isSqlOpen ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                        </Button>
                      </div>
                    </CollapsibleTrigger>

                    <CollapsibleContent>
                      <div className="relative p-3 bg-black text-green-400 rounded-b-md overflow-auto h-auto">
                      <Button
                        variant="ghost"
                        size="icon"
                        className="absolute top-2 right-2 h-8 w-8 text-white hover:text-white hover:bg-white/10"
                        title="Copiar SQL"
                        onClick={() => copyToClipboard(sqlQuery)}
                      >
                      <Copy className="h-4 w-4" />
                      </Button>
                      <pre className="text-sm pr-10 whitespace-pre-wrap break-all">{sqlQuery}</pre>
                     </div>
                     </CollapsibleContent>


                    {/* <CollapsibleContent>
                      <div className="relative p-3 bg-black text-green-400 rounded-b-md overflow-x-auto">
                        <Button
                          variant="ghost"
                          size="icon"
                          className="absolute top-2 right-2 h-8 w-8 text-white hover:text-white hover:bg-white/10"
                          title="Copiar SQL"
                          onClick={() => copyToClipboard(sqlQuery)}
                        >
                          <Copy className="h-4 w-4" />
                        </Button>
                        <pre className="text-sm pr-10">{sqlQuery}</pre>
                      </div>
                    </CollapsibleContent> */}

                  </Collapsible>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Modal de Senha do Database */}
        <Dialog open={isPasswordModalOpen} onOpenChange={setIsPasswordModalOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Senha do Banco de Dados</DialogTitle>
              <DialogDescription>
                Digite a senha para conectar ao banco de dados {selectedDb?.name}.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Input
                  type="password"
                  placeholder="Digite a senha do banco de dados"
                  value={dbPassword}
                  onChange={(e) => setDbPassword(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handlePasswordSubmit()}
                />
                {passwordError && (
                  <p className="text-sm text-red-500">{passwordError}</p>
                )}
              </div>
            </div>
            <div className="flex justify-end gap-3">
              <Button
                variant="outline"
                onClick={() => setIsPasswordModalOpen(false)}
              >
                Cancelar
              </Button>
              <Button onClick={handlePasswordSubmit}>
                Confirmar
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  )
}
