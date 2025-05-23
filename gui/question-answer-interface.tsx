"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Copy, Database, ChevronDown, ChevronUp, Code, Sparkles } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"
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

  // Função para buscar os databases da API
  const fetchDatabases = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'}/api/databases/`, {
        credentials: 'include', // Importante para enviar cookies
      })
      
      if (!response.ok) {
        throw new Error('Failed to fetch databases')
      }

      const data = await response.json()
      setDatabases(data)
      
      // Se houver um database ID na URL, seleciona ele
      const dbId = searchParams.get("db")
      if (dbId) {
        const selectedDatabase = data.find((db: Database) => db.id === dbId)
        if (selectedDatabase) {
          setSelectedDb(selectedDatabase)
        }
      } else if (data.length > 0) {
        // Se não houver ID na URL mas houver databases, seleciona o primeiro
        setSelectedDb(data[0])
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

  const handleSubmit = async () => {
    if (!question.trim()) return

    setIsLoading(true)

    // Aqui você terá acesso ao tipo de template selecionado através de selectedTemplate?.apiValue
    const templateType = selectedTemplate?.apiValue || "text_to_sql" // default para text_to_sql se nenhum template estiver selecionado

    // Simulando uma resposta da API com SQL gerado
    setTimeout(() => {
      // TODO: Enviar templateType para a API quando implementar a chamada real
      console.log("Template type to be sent to API:", templateType)

      // Exemplo de SQL que seria gerado baseado na pergunta
      const generatedSql = `SELECT 
  c.customer_name,
  SUM(o.total_amount) as total_purchases
FROM ${selectedDb?.name.toLowerCase().replace(" ", "_")}.customers c
JOIN ${selectedDb?.name.toLowerCase().replace(" ", "_")}.orders o
  ON c.customer_id = o.customer_id
WHERE o.purchase_date > '2023-01-01'
GROUP BY c.customer_id, c.customer_name
ORDER BY total_purchases DESC
LIMIT 10;`

      setSqlQuery(generatedSql)

      setAnswer(
        `Com base na sua pergunta: "${question}" consultando o banco de dados "${selectedDb?.name}"\n\nEncontrei os 10 clientes com as maiores compras desde janeiro de 2023. O cliente João Silva lidera com R$15.750 em compras, seguido por Maria Oliveira com R$12.320. A média de compras destes clientes é de R$8.940.\n\nOs dados completos estão disponíveis na tabela abaixo.`,
      )
      setIsLoading(false)
      setIsSqlOpen(true) // Mostrar SQL automaticamente na primeira resposta
    }, 1000)
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

  return (
    <div className="flex-1 flex flex-col items-center p-6 gap-6 overflow-y-auto">
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
            <div className="space-y-2">
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
                      <Button variant="outline" className="gap-2" disabled={isLoadingDatabases}>
                        <Database className="h-4 w-4" />
                        {isLoadingDatabases ? (
                          "Carregando..."
                        ) : selectedDb ? (
                          selectedDb.name
                        ) : (
                          "Selecione um banco"
                        )}
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="start">
                      {databases.map((db) => (
                        <DropdownMenuItem key={db.id} onClick={() => setSelectedDb(db)} className="cursor-pointer">
                          {db.name}
                        </DropdownMenuItem>
                      ))}
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
                        {selectedTemplate ? selectedTemplate.name : "Escolher Template"}
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
                  disabled={!question.trim() || isLoading || !selectedDb} 
                  className="px-8"
                >
                  {isLoading ? "Processando..." : "Enviar"}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {answer && (
          <Card className="mt-6 shadow-md">
            <CardContent className="pt-6">
              <div className="space-y-4">
                {/* Resposta em linguagem natural com ícone de cópia no canto superior direito */}
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
                    </CollapsibleContent>
                  </Collapsible>
                )}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
