"use client"

import { useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Copy, ChevronLeft, ChevronDown, ChevronUp, Code, Database, Clock } from "lucide-react"
import Link from "next/link"
import { useParams, useRouter } from "next/navigation"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"

// Dados de exemplo para demonstração
const sampleQueries = [
  {
    id: "q1",
    databaseId: "db1",
    databaseName: "Vendas",
    question: "Quais são os 10 clientes com maior valor de compra desde janeiro de 2023?",
    answer: `Com base na sua pergunta consultando o banco de dados "Vendas"

Encontrei os 10 clientes com as maiores compras desde janeiro de 2023. O cliente João Silva lidera com R$15.750 em compras, seguido por Maria Oliveira com R$12.320. A média de compras destes clientes é de R$8.940.

Os dados completos estão disponíveis na tabela abaixo.`,
    sqlQuery: `SELECT 
  c.customer_name,
  SUM(o.total_amount) as total_purchases
FROM vendas.customers c
JOIN vendas.orders o
  ON c.customer_id = o.customer_id
WHERE o.purchase_date > '2023-01-01'
GROUP BY c.customer_id, c.customer_name
ORDER BY total_purchases DESC
LIMIT 10;`,
    timestamp: "2023-08-15T14:30:00",
    formattedDate: "15/08/2023 14:30",
  },
  {
    id: "q2",
    databaseId: "db1",
    databaseName: "Vendas",
    question: "Qual é o produto mais vendido por região?",
    answer: `Com base na sua pergunta consultando o banco de dados "Vendas"

Analisei as vendas por região e identifiquei os produtos mais vendidos em cada uma:

- Sul: Notebook Dell XPS (1.245 unidades)
- Sudeste: iPhone 13 (2.890 unidades)
- Centro-Oeste: Smart TV Samsung (980 unidades)
- Norte: Ar Condicionado Inverter (760 unidades)
- Nordeste: Smartphone Samsung Galaxy (1.560 unidades)

O iPhone 13 é o produto com maior volume de vendas em uma única região (Sudeste).`,
    sqlQuery: `WITH RankedProducts AS (
  SELECT 
    r.region_name,
    p.product_name,
    SUM(oi.quantity) as total_quantity,
    ROW_NUMBER() OVER (PARTITION BY r.region_name ORDER BY SUM(oi.quantity) DESC) as rank
  FROM vendas.regions r
  JOIN vendas.stores s ON r.region_id = s.region_id
  JOIN vendas.orders o ON s.store_id = o.store_id
  JOIN vendas.order_items oi ON o.order_id = oi.order_id
  JOIN vendas.products p ON oi.product_id = p.product_id
  GROUP BY r.region_name, p.product_name
)
SELECT 
  region_name,
  product_name,
  total_quantity
FROM RankedProducts
WHERE rank = 1
ORDER BY total_quantity DESC;`,
    timestamp: "2023-08-14T10:15:00",
    formattedDate: "14/08/2023 10:15",
  },
]

export default function QueryDetailsPage() {
  const params = useParams()
  const router = useRouter()
  const queryId = params.id as string

  // Estado para controlar a visibilidade do SQL
  const [isSqlOpen, setIsSqlOpen] = useState(true)

  // Encontrar a consulta pelos dados de exemplo
  const query = sampleQueries.find((q) => q.id === queryId)

  // Se a consulta não for encontrada, redirecionar para a página de consultas
  if (!query) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-6">
        <div className="text-center">
          <h2 className="text-xl font-bold mb-2">Consulta não encontrada</h2>
          <p className="text-muted-foreground mb-4">A consulta que você está procurando não existe ou foi removida.</p>
          <Button asChild>
            <Link href="/queries">Voltar para Consultas</Link>
          </Button>
        </div>
      </div>
    )
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

  return (
    <div className="flex-1 flex flex-col p-6 overflow-y-auto">
      <div className="w-full max-w-4xl mx-auto">
        {/* Navegação */}
        <div className="mb-6">
          <Button variant="ghost" className="gap-1 pl-0" asChild>
            <Link href="/queries">
              <ChevronLeft className="h-4 w-4" />
              Voltar para Consultas
            </Link>
          </Button>
        </div>

        {/* Informações da consulta */}
        <div className="mb-6">
          <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2">
            <Database className="h-4 w-4" />
            <span>{query.databaseName}</span>
            <span className="mx-1">•</span>
            <Clock className="h-4 w-4" />
            <span>{query.formattedDate}</span>
          </div>
          <h1 className="text-2xl font-bold">{query.question}</h1>
        </div>

        {/* Resposta */}
        <Card className="mb-4 shadow-md">
          <CardContent className="pt-6">
            <div className="space-y-4">
              {/* Resposta em linguagem natural com ícone de cópia no canto superior direito */}
              <div className="relative p-4 bg-muted/50 rounded-lg min-h-[150px]">
                <Button
                  variant="ghost"
                  size="icon"
                  className="absolute top-2 right-2 h-8 w-8"
                  title="Copiar resposta"
                  onClick={() => copyToClipboard(query.answer)}
                >
                  <Copy className="h-4 w-4" />
                </Button>
                <p className="text-sm whitespace-pre-wrap pr-10">{query.answer}</p>
              </div>

              {/* SQL Query colapsável */}
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
                      onClick={() => copyToClipboard(query.sqlQuery)}
                    >
                      <Copy className="h-4 w-4" />
                    </Button>
                    <pre className="text-sm pr-10">{query.sqlQuery}</pre>
                  </div>
                </CollapsibleContent>
              </Collapsible>
            </div>
          </CardContent>
        </Card>

        {/* Botões de ação */}
        <div className="flex justify-between">
          <Button variant="outline" asChild>
            <Link href={`/queries?db=${query.databaseId}`}>Ver todas as consultas</Link>
          </Button>
          <Button asChild>
            <Link href={`/?db=${query.databaseId}&question=${encodeURIComponent(query.question)}`}>
              Refazer consulta
            </Link>
          </Button>
        </div>
      </div>
    </div>
  )
}
