// app/databases/page.tsx
"use client";

import ClientLayout from "../ClientLayout";          // ajusta o caminho relativo
import { DatabaseFormDialog } from "@/components/database-form-dialog";

export default function DatabasesPage() {
  return (
    <ClientLayout>
      {/* Força o diálogo aberto */}
      <DatabaseFormDialog open={true} onOpenChange={() => { /* trata o fechar */ }} />
    </ClientLayout>
  );
}
