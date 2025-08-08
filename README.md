# Luigui: Democratizando o Acesso a Dados com IA Generativa

Luigui é um sistema web inovador que permite a qualquer pessoa, mesmo sem conhecimento técnico, consultar bancos de dados utilizando apenas linguagem natural. Desenvolvido como um projeto de TCC, Luigui visa democratizar o acesso a dados estruturados em empresas e instituições, tornando o uso de bancos de dados mais acessível para áreas como RH, educação e marketing.

Por exemplo, você pode perguntar: "Quais alunos estão matriculados na turma de Estruturas de Dados?" e Luigui gerará automaticamente uma consulta SQL pronta para ser executada.

Para tornar isso possível, Luigui combina o poder da Inteligência Artificial Generativa, utilizando Large Language Models (LLMs) com a técnica de Retrieval-Augmented Generation (RAG). Essa combinação garante que o modelo tenha acesso ao contexto real dos dados antes de gerar a query, reduzindo erros e aumentando a precisão das respostas.




## Técnicas Interessantes

Este projeto apresenta várias técnicas interessantes que aprimoram as práticas de desenvolvimento web e a interação com dados:

*   **Arquitetura Full-Stack (Django & Next.js)**: Luigui emprega uma arquitetura full-stack desacoplada. Django alimenta a robusta API de backend, lidando com a lógica de dados e servindo como um provedor de API RESTful. Next.js, um framework React, constrói a GUI interativa e performática de frontend. Essa separação permite o desenvolvimento e a escalabilidade independentes de ambas as camadas.

*   **Interface Text-to-SQL com IA Generativa e RAG**: Uma característica central do Luigui é sua capacidade de traduzir linguagem natural em consultas SQL. Isso é alcançado através da combinação de Large Language Models (LLMs) com a técnica de Retrieval-Augmented Generation (RAG). O RAG permite que o modelo acesse e utilize o contexto real dos esquemas de banco de dados, garantindo que as consultas SQL geradas sejam precisas e relevantes. 

*   **Aplicativos Django Modulares**: O backend Django é estruturado em aplicativos modulares (por exemplo, `api`, `src/core`). Isso promove a reutilização de código, a manutenibilidade e a escalabilidade, dividindo o aplicativo em componentes menores e gerenciáveis.

*   **Compilação SCSS com Gulp**: O projeto utiliza Gulp para compilar arquivos SCSS em CSS, otimizando o fluxo de trabalho de estilo. Isso permite um CSS mais organizado e manutenível com recursos como variáveis, aninhamento e mixins. 

*   **Containerização com Docker**: Toda a aplicação (componentes Django e Next.js) é containerizada usando Docker. Isso proporciona um ambiente consistente e isolado para desenvolvimento, teste e implantação, eliminando problemas de "funciona na minha máquina" e simplificando a implantação.

*   **Implantação com Gunicorn e Nginx**: O backend Django é configurado para implantação em produção usando Gunicorn como um servidor HTTP WSGI e Nginx como um proxy reverso. Essa configuração é altamente performática e escalável para servir aplicativos Django.


## Tecnologias e Bibliotecas Não Óbvias

Além dos frameworks principais Django e Next.js, Luigui incorpora várias tecnologias e bibliotecas que podem ser de particular interesse para desenvolvedores experientes:

*   **PostgreSQL + PGVector**: Utilizado para armazenamento de dados e vetores. A extensão PGVector permite o armazenamento eficiente de embeddings de alta dimensão, esse=ncial para a funcionalidade RAG.

*   **LlamaIndex**: Uma estrutura de dados flexível e extensível para construir aplicações de LLM. No Luigui, é usado para o pipeline RAG com embeddings dos esquemas de tabelas, garantindo que o modelo tenha acesso ao contexto correto do banco de dados.

*   **API da OpenAI**: A interface para interagir com os modelos de linguagem da OpenAI, que são a base para a funcionalidade de IA Generativa do Luigui.

*   **Shadcn/UI**: Um conjunto de componentes de interface de usuário reutilizáveis e acessíveis, construídos com Tailwind CSS e Radix UI. É provável que seja usado no frontend Next.js para criar uma experiência de usuário moderna e responsiva.

*   **uv**: A presença de `pyproject.toml` e `requirements.txt` sugere o uso de `uv`, um instalador e resolvedor de pacotes Python rápido. Isso pode acelerar significativamente o gerenciamento de dependências para o backend Python.

*   **psycopg2**: Este é o adaptador PostgreSQL para Python. Sua presença indica que o backend Django é projetado para funcionar com bancos de dados PostgreSQL. [Documentação do psycopg2.

*   **Django REST Framework**: A estrutura do diretório `api` com `serializer.py`, `views.py` e `urls.py` indica que o Django REST Framework (DRF) é usado para construir APIs web robustas e escaláveis para o backend. O DRF simplifica a criação de APIs RESTful sobre o Django.

*   **Next.js**: Um framework React para construir aplicações web renderizadas no lado do servidor (SSR) e geradas estaticamente. Ele fornece recursos como roteamento baseado em sistema de arquivos, rotas de API e tratamento otimizado de imagens.

*   **Tailwind CSS**: O arquivo `tailwind.config.ts` no diretório `gui` sugere o uso de Tailwind CSS, um framework CSS utilitário. Ele permite o desenvolvimento rápido de UI, fornecendo classes de utilidade de baixo nível diretamente na marcação.

*   **TypeScript**: A presença de arquivos `.ts` e `.tsx` no diretório `gui` indica que o frontend é desenvolvido usando TypeScript, um superconjunto de JavaScript que adiciona tipagem estática. Isso aprimora a qualidade do código, a manutenibilidade e a experiência do desenvolvedor.




## Estrutura do Projeto

O projeto segue uma estrutura bem organizada, típica para aplicações full-stack, com clara separação de responsabilidades entre o backend Django e o frontend Next.js:

```
.
├── gui/
│   ├── app/
│   │   ├── databases/
│   │   ├── login/
│   │   ├── queries/
│   │   ├── register/
│   │   └── templates/
│   ├── components/
│   ├── config/
│   ├── contexts/
│   ├── hooks/
│   ├── public/
│   ├── services/
│   └── styles/
├── scripts/
├── src/
│   ├── api/
│   │   ├── migrations/
│   │   └── services/
│   └── core/
├── .env.example
├── .gitignore
├── .python-version
├── docker-compose.yml
├── pyproject.toml
├── requirements.txt
└── test.py
```

### Descrições dos Diretórios

*   **`gui/`**: Este diretório contém a aplicação frontend Next.js.
    *   **`gui/app/`**: Lógica central da aplicação e páginas para o aplicativo Next.js.
        *   **`gui/app/databases/`**: Provavelmente lida com interações ou configurações relacionadas ao banco de dados específicas do frontend.
        *   **`gui/app/login/`**: Contém componentes e lógica para o login do usuário.
        *   **`gui/app/queries/`**: Gerencia a busca de dados e consultas da API de backend.
        *   **`gui/app/register/`**: Contém componentes e lógica para o registro do usuário.
        *   **`gui/app/templates/`**: Modelos de frontend ou componentes de layout.
    *   **`gui/components/`**: Componentes de UI reutilizáveis para a aplicação Next.js.
    *   **`gui/config/`**: Arquivos de configuração do frontend.
    *   **`gui/contexts/`**: Implementações da React Context API para gerenciamento de estado global.
    *   **`gui/hooks/`**: Hooks React personalizados para lógica reutilizável.
    *   **`gui/public/`**: Ativos estáticos servidos diretamente pelo Next.js (por exemplo, imagens, fontes).
    *   **`gui/services/`**: Serviços de frontend para interagir com a API de backend.
    *   **`gui/styles/`**: Estilos globais ou definições de tema para a aplicação Next.js.
*   **`scripts/`**: Contém vários scripts de utilidade para automação, configuração ou tarefas de implantação.
*   **`src/`**: O diretório principal do código-fonte para o projeto backend Django.
    *   **`src/api/`**: Abriga o código relacionado à API, implementando endpoints RESTful usando o Django REST Framework. Isso inclui migrações de banco de dados (`migrations/`) e lógica específica de serviço (`services/`), particularmente para funcionalidades text-to-SQL.
    *   **`src/core/`**: Contém as configurações principais do projeto Django, configurações de URL e outras configurações globais.
*   **`.env.example`**: Um arquivo de modelo para variáveis de ambiente, útil para configurar o aplicativo em diferentes ambientes.
*   **`docker-compose.yml`**: Define o aplicativo Docker de múltiplos contêineres, orquestrando serviços como o aplicativo Django, Next.js e, potencialmente, um banco de dados.
*   **`pyproject.toml`**: Arquivo de configuração para projetos Python, potencialmente usado por ferramentas como `uv` para gerenciamento de dependências e metadados do projeto.
*   **`requirements.txt`**: Lista as dependências Python necessárias para o backend Django, usadas por `pip` ou `uv` para instalação.



## Tecnologias Utilizadas

*   **Django** (backend)
*   **Next.js**, **Tailwind CSS**, **Shadcn/UI** (frontend)
*   **PostgreSQL** + **PGVector** (armazenamento de dados e vetores)
*   **LlamaIndex** (pipeline RAG com embeddings dos esquemas de tabelas)
*   **API da OpenAI**



****
