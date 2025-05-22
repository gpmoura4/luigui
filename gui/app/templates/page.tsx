"use client"

import { Card, CardContent, CardFooter } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ArrowRight, Sparkles, Zap, Search, WrenchIcon } from "lucide-react"
import { useRouter } from "next/navigation"

// Lista de templates disponíveis
const templates = [
  {
    id: "generate",
    name: "Text-To-SQL",
    description: "Gere uma consulta SQL a partir de uma pergunta em linguagem natural.",
    icon: Sparkles,
    prompt: "Gere uma consulta SQL para responder a seguinte pergunta: ",
    color: "bg-blue-500/10 text-blue-500",
  },
  {
    id: "optimize",
    name: "Otimizar Consulta",
    description: "Otimize uma consulta SQL existente para melhorar o desempenho.",
    icon: Zap,
    prompt: "Otimize a seguinte consulta SQL para melhorar o desempenho: ",
    color: "bg-amber-500/10 text-amber-500",
  },
  {
    id: "explain",
    name: "Explicar Consulta",
    description: "Obtenha uma explicação detalhada de como uma consulta SQL funciona.",
    icon: Search,
    prompt: "Explique em detalhes como a seguinte consulta SQL funciona: ",
    color: "bg-green-500/10 text-green-500",
  },
  {
    id: "correct",
    name: "Corrigir Consulta",
    description: "Corrija erros em uma consulta SQL existente.",
    icon: WrenchIcon,
    prompt: "Corrija os erros na seguinte consulta SQL: ",
    color: "bg-purple-500/10 text-purple-500",
  },
]

export default function TemplatesPage() {
  const router = useRouter()

  const handleTemplateClick = (template: (typeof templates)[0]) => {
    // Redirecionar para a tela de Nova Consulta com o template selecionado
    router.push(`/?template=${template.id}`)
  }

  return (
    <div className="flex-1 flex flex-col p-6 overflow-y-auto">
      <div className="w-full max-w-6xl mx-auto">
        {/* Cabeçalho com título */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold mb-2">Templates</h1>
          <p className="text-muted-foreground">
            Escolha um template para iniciar rapidamente uma nova consulta com um prompt pré-definido.
          </p>
        </div>

        {/* Grid de templates */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {templates.map((template) => (
            <Card
              key={template.id}
              className="overflow-hidden transition-all hover:shadow-md cursor-pointer"
              onClick={() => handleTemplateClick(template)}
            >
              <CardContent className="p-6">
                <div className="flex flex-col gap-4">
                  <div className={`h-12 w-12 rounded-lg ${template.color} flex items-center justify-center`}>
                    <template.icon className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="font-medium text-lg">{template.name}</h3>
                    <p className="text-muted-foreground mt-1">{template.description}</p>
                  </div>
                </div>
              </CardContent>
              <CardFooter className="bg-muted/20 p-4 flex justify-end">
                <Button variant="ghost" size="sm" className="gap-1">
                  Usar template
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      </div>
    </div>
  )
}
