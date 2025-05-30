"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Textarea } from "@/components/ui/textarea"
import { Copy, ArrowLeft, ArrowRight, Database, FileCode } from "lucide-react"
import { createDatabase } from "@/services/database"
import { useToast } from "@/components/ui/use-toast"

interface DatabaseFormDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onDatabaseChange?: () => void
  database?: {
    id: string
    name: string
    type: "complete" | "minimal"
    host?: string
    port?: string
    username?: string
    db_name?: string
    schemas?: string
  }
}

export function DatabaseFormDialog({ open, onOpenChange, onDatabaseChange, database }: DatabaseFormDialogProps) {
  const { toast } = useToast()
  const [step, setStep] = useState(1)
  const [name, setName] = useState(database?.name || "")
  const [connectionType, setConnectionType] = useState<"direct" | "schema">(
    database?.type === "complete" ? "direct" : "schema"
  )
  const [host, setHost] = useState(database?.host || "")
  const [port, setPort] = useState(database?.port || "")
  const [username, setUsername] = useState(database?.username || "")
  const [password, setPassword] = useState("")
  const [schema, setSchema] = useState(database?.schemas || "")

  // Script de extração de esquema
  const schemaExtractionScript = `SELECT json_agg(
  json_build_object(
    'schema_name', table_schema,
    'table_name', table_name,
    'column_name', column_name,
    'column_type', data_type
  )
)
FROM information_schema.columns
WHERE table_schema NOT IN ('information_schema', 'pg_catalog', 'pg_toast');`

  // Função para copiar o script para a área de transferência
  const copyScript = () => {
    navigator.clipboard
      .writeText(schemaExtractionScript)
      .then(() => {
        console.log("Script copiado para a área de transferência")
        // Aqui você poderia adicionar uma notificação de sucesso
      })
      .catch((err) => {
        console.error("Erro ao copiar script: ", err)
      })
  }

  // Função para avançar para a próxima etapa
  const nextStep = () => {
    setStep(step + 1)
  }

  // Função para voltar para a etapa anterior
  const prevStep = () => {
    setStep(step - 1)
  }

  // Função para resetar o formulário ao fechar
  const handleClose = () => {
    setStep(1)
    onOpenChange(false)
  }

  // Função para salvar o banco de dados
  const handleSave = async () => {
    try {
      console.log("Preparing data to save...")
      
      const databaseData = {
        name,
        type: connectionType === "direct" ? "complete" as const : "minimal" as const,
        ...(connectionType === "direct"
          ? {
              host,
              port,
              username,
              password,
              db_name: name,
            }
          : {
              host: null,
              port: null,
              username: null,
              db_name: null,
              schemas: schema,
            }),
      }

      console.log("Database data to be sent:", databaseData)
      
      await createDatabase(databaseData)
      toast({
        title: "Sucesso!",
        description: "Banco de dados criado com sucesso.",
      })
      onDatabaseChange?.()
      handleClose()
    } catch (error) {
      console.error("Error saving database:", error)
      toast({
        title: "Erro!",
        description: error instanceof Error ? error.message : "Erro ao criar banco de dados. Tente novamente.",
        variant: "destructive",
      })
    }
  }

  // Verificar se o botão "Próximo" deve estar desabilitado
  const isNextDisabled = () => {
    if (step === 1) return !name.trim()
    if (step === 2) return !connectionType
    if (step === 3 && connectionType === "direct") {
      return !host.trim() || !port.trim() || !username.trim()
    }
    if (step === 3 && connectionType === "schema") {
      return !schema.trim()
    }
    return false
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {database ? "Editar Banco de Dados" : "Novo Banco de Dados"}
            {!database && ` - Etapa ${step} de ${connectionType === "direct" ? 3 : 3}`}
          </DialogTitle>
          <DialogDescription>
            {step === 1 && "Dê um nome para a sua conexão de banco de dados."}
            {step === 2 && "Escolha como você deseja configurar seu banco de dados."}
            {step === 3 && connectionType === "direct" && "Forneça os detalhes de conexão do seu banco de dados."}
            {step === 3 &&
              connectionType === "schema" &&
              "Execute o script abaixo no seu banco de dados e cole o resultado."}
          </DialogDescription>
        </DialogHeader>

        <div className="py-4">
          {/* Etapa 1: Nome da Conexão */}
          {step === 1 && (
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Nome da Conexão</Label>
                <Input
                  id="name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Ex: Banco de Dados de Vendas"
                  required
                />
                <p className="text-xs text-muted-foreground">
                  Este nome será usado para identificar seu banco de dados no sistema.
                </p>
              </div>
            </div>
          )}

          {/* Etapa 2: Tipo de Conexão */}
          {step === 2 && (
            <div className="space-y-4">
              <RadioGroup
                value={connectionType}
                onValueChange={(value) => setConnectionType(value as "direct" | "schema")}
              >
                <div className="flex items-start space-x-3 space-y-0 rounded-md border p-4 cursor-pointer hover:bg-muted/50">
                  <RadioGroupItem value="direct" id="direct" className="mt-1" />
                  <div className="space-y-1">
                    <Label htmlFor="direct" className="font-medium cursor-pointer flex items-center gap-2">
                      <Database className="h-4 w-4" />
                      Conexão Direta com Banco de Dados
                    </Label>
                    <p className="text-sm text-muted-foreground">
                      Conecte diretamente ao seu banco de dados para executar as consultas geradas. Requer acesso ao
                      servidor de banco de dados.
                    </p>
                  </div>
                </div>
                <div className="flex items-start space-x-3 space-y-0 rounded-md border p-4 cursor-pointer hover:bg-muted/50">
                  <RadioGroupItem value="schema" id="schema" className="mt-1" />
                  <div className="space-y-1">
                    <Label htmlFor="schema" className="font-medium cursor-pointer flex items-center gap-2">
                      <FileCode className="h-4 w-4" />
                      Fornecer Esquemas
                    </Label>
                    <p className="text-sm text-muted-foreground">
                      Forneça apenas os esquemas do banco de dados. As consultas serão geradas, mas não executadas
                      automaticamente. Opção mais simples e segura.
                    </p>
                  </div>
                </div>
              </RadioGroup>
            </div>
          )}

          {/* Etapa 3A: Detalhes da Conexão (se Direct Connection) */}
          {step === 3 && connectionType === "direct" && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="host">Host</Label>
                  <Input
                    id="host"
                    value={host}
                    onChange={(e) => setHost(e.target.value)}
                    placeholder="Ex: localhost ou db.example.com"
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="port">Porta</Label>
                  <Input
                    id="port"
                    value={port}
                    onChange={(e) => setPort(e.target.value)}
                    placeholder="Ex: 5432"
                    required
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="username">Usuário</Label>
                <Input
                  id="username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Ex: postgres"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Senha</Label>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Digite a senha do banco de dados"
                />
                <p className="text-xs text-muted-foreground">
                  A senha é armazenada de forma segura e nunca é compartilhada.
                </p>
              </div>
            </div>
          )}

          {/* Etapa 3B: Fornecer Esquemas (se Provide Schemas) */}
          {step === 3 && connectionType === "schema" && (
            <div className="space-y-4">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label>Script de Extração de Esquema</Label>
                  <Button variant="outline" size="sm" className="gap-1" onClick={copyScript}>
                    <Copy className="h-3.5 w-3.5" />
                    Copiar
                  </Button>
                </div>
                <div className="bg-black text-green-400 p-3 rounded-md overflow-x-auto max-w-full">
                  <pre className="text-xs whitespace-pre-wrap break-all">{schemaExtractionScript}</pre>
                </div>
                <p className="text-xs text-muted-foreground">
                  Execute este script no seu banco de dados e cole o resultado abaixo.
                </p>
              </div>
              <div className="space-y-2">
                <Label htmlFor="schema">Esquema Extraído</Label>
                <Textarea
                  id="schema"
                  value={schema}
                  onChange={(e) => setSchema(e.target.value)}
                  placeholder="Cole aqui o resultado do script de extração..."
                  className="min-h-[150px] max-h-[300px] font-mono text-xs resize-y overflow-auto w-full"
                  required
                />
              </div>
            </div>
          )}
        </div>

        <DialogFooter className="flex justify-between sm:justify-between">
          <div>
            {step > 1 && (
              <Button type="button" variant="outline" onClick={prevStep} className="gap-1">
                <ArrowLeft className="h-4 w-4" />
                Voltar
              </Button>
            )}
          </div>
          <div className="flex gap-2">
            <Button type="button" variant="outline" onClick={handleClose}>
              Cancelar
            </Button>
            {step < (connectionType === "direct" ? 3 : 3) ? (
              <Button type="button" onClick={nextStep} disabled={isNextDisabled()} className="gap-1">
                Próximo
                <ArrowRight className="h-4 w-4" />
              </Button>
            ) : (
              <Button type="button" onClick={handleSave} disabled={isNextDisabled()}>
                Concluir
              </Button>
            )}
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
