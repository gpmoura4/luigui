# Luigui: Uma Aplicação Web Baseada em Django

Luigui é uma aplicação web construída sobre o framework Django, projetada para fornecer uma base robusta e escalável para vários projetos web. Ela aproveita uma arquitetura modular, integrando um design moderno do Bootstrap 4 do Argon Dashboard. Este projeto enfatiza código limpo, autenticação baseada em sessão e prontidão para implantação com Docker e Gunicorn/Nginx.




## Técnicas Interessantes

Este projeto apresenta várias técnicas interessantes que aprimoram as práticas de desenvolvimento web:

*   **Aplicativos Django Modulares**: O projeto é estruturado em aplicativos Django modulares (por exemplo, `api`, `apps/authentication`, `apps/home`). Isso promove a reutilização de código, a manutenibilidade e a escalabilidade, dividindo o aplicativo em componentes menores e gerenciáveis. [Saiba mais sobre aplicativos Django](https://docs.djangoproject.com/en/stable/intro/tutorial01/#creating-polls-app).

*   **Compilação SCSS com Gulp**: Utiliza Gulp para compilar arquivos SCSS em CSS. Isso simplifica o fluxo de trabalho de estilo, permitindo que os desenvolvedores escrevam CSS mais organizado e manutenível com recursos como variáveis, aninhamento e mixins. [Explore Gulp](https://gulpjs.com/) e [SCSS (Sass)](https://sass-lang.com/documentation/scss).

*   **Autenticação Baseada em Sessão**: Implementa autenticação segura baseada em sessão, uma prática padrão para gerenciar sessões de usuário e garantir a integridade dos dados. [Entenda o gerenciamento de sessão no Django](https://docs.djangoproject.com/en/stable/topics/auth/default/#session-authentication).

*   **Containerização com Docker**: O aplicativo é containerizado usando Docker, fornecendo um ambiente consistente e isolado para desenvolvimento, teste e implantação. Isso elimina problemas de "funciona na minha máquina" e simplifica a implantação. [Aprofunde-se no Docker](https://docs.docker.com/get-started/).

*   **Implantação com Gunicorn e Nginx**: Configurado para implantação em produção usando Gunicorn como um servidor HTTP WSGI e Nginx como um proxy reverso. Essa configuração é altamente performática e escalável para servir aplicativos Django. [Saiba mais sobre Gunicorn](https://gunicorn.org/) e [Nginx](https://nginx.org/en/docs/).




## Tecnologias e Bibliotecas Não Óbvias

Além do framework Django principal, Luigui incorpora várias tecnologias e bibliotecas que podem ser de particular interesse para desenvolvedores experientes:

*   **Argon Dashboard**: Este projeto usa o Argon Dashboard, um template de administração Bootstrap 4 gratuito, para sua interface de usuário. Ele fornece um rico conjunto de componentes pré-construídos e um design moderno, acelerando o desenvolvimento frontend. [Explore o Argon Dashboard](https://www.creative-tim.com/product/argon-dashboard-django).

*   **Gulp**: Um kit de ferramentas JavaScript usado para automatizar tarefas demoradas no fluxo de trabalho de desenvolvimento, como compilação SCSS, minificação e recarregamento ao vivo. [Site oficial do Gulp.js](https://gulpjs.com/).

*   **uv**: Embora não explicitamente detalhado no conteúdo do diretório `src` fornecido, os arquivos `pyproject.toml` e `requirements.txt` sugerem o uso de `uv`, um instalador e resolvedor de pacotes Python rápido. Isso pode acelerar significativamente o gerenciamento de dependências. [Repositório uv no GitHub](https://github.com/astral-sh/uv).

*   **psycopg2**: Este é o adaptador PostgreSQL para Python. Sua presença indica que o projeto foi projetado para funcionar com bancos de dados PostgreSQL, um poderoso sistema de banco de dados objeto-relacional de código aberto. [Documentação do psycopg2](https://www.psycopg.org/docs/).

*   **Pillow**: Uma ramificação amigável da PIL (Python Imaging Library), Pillow adiciona recursos de processamento de imagem ao Python. É comumente usado para tarefas como redimensionamento, corte e adição de marcas d'água a imagens. [Documentação do Pillow](https://pillow.readthedocs.io/en/stable/).

*   **Django REST Framework**: Dada a estrutura do diretório `api` com `serializer.py`, `views.py` e `urls.py`, é altamente provável que o Django REST Framework (DRF) seja usado para construir APIs web robustas e escaláveis. O DRF simplifica a criação de APIs RESTful sobre o Django. [Documentação do Django REST Framework](https://www.django-rest-framework.org/).




## Estrutura do Projeto

O projeto segue uma estrutura bem organizada, típica para aplicações Django, com clara separação de responsabilidades:

```
.
├── scripts/
├── src/
│   ├── api/
│   │   ├── migrations/
│   │   └── services/
│   ├── apps/
│   │   ├── authentication/
│   │   ├── home/
│   │   ├── static/
│   │   └── templates/
│   ├── core/
│   ├── media/
│   ├── nginx/
│   └── staticfiles/
├── .env.example
├── .gitignore
├── .python-version
├── docker-compose.yml
├── pyproject.toml
├── requirements.txt
└── test.py
```

### Descrições dos Diretórios

*   **`scripts/`**: Contém vários scripts de utilidade para automação, configuração ou tarefas de implantação.
*   **`src/`**: O diretório principal do código-fonte para o projeto Django.
    *   **`src/api/`**: Abriga o código relacionado à API, provavelmente implementando endpoints RESTful usando o Django REST Framework. Isso inclui migrações de banco de dados (`migrations/`) e lógica específica de serviço (`services/`).
    *   **`src/apps/`**: Contém aplicativos Django individuais que compõem o projeto.
        *   **`src/apps/authentication/`**: Lida com a autenticação do usuário, incluindo login, registro e gerenciamento de sessão.
        *   **`src/apps/home/`**: Provavelmente contém a lógica central do aplicativo e as visualizações para as partes principais da aplicação voltadas para o usuário.
        *   **`src/apps/static/`**: Armazena ativos estáticos como CSS, JavaScript e imagens que são servidos diretamente pelo servidor web.
        *   **`src/apps/templates/`**: Contém modelos HTML usados pelo Django para renderizar páginas web dinâmicas.
    *   **`src/core/`**: Contém as configurações principais do projeto, configurações de URL e outras configurações globais.
    *   **`src/media/`**: Destinado a arquivos de mídia enviados pelo usuário.
    *   **`src/nginx/`**: Arquivos de configuração para o servidor web Nginx, usados para servir arquivos estáticos e proxy de requisições para o Gunicorn.
    *   **`src/staticfiles/`**: Coleta todos os arquivos estáticos de vários aplicativos Django em um único local para um serviço eficiente em produção.
*   **`.env.example`**: Um arquivo de modelo para variáveis de ambiente, útil para configurar o aplicativo em diferentes ambientes.
*   **`docker-compose.yml`**: Define o aplicativo Docker de múltiplos contêineres, orquestrando serviços como o aplicativo Django, PostgreSQL e Nginx.
*   **`pyproject.toml`**: Arquivo de configuração para projetos Python, potencialmente usado por ferramentas como `uv` para gerenciamento de dependências e metadados do projeto.
*   **`requirements.txt`**: Lista as dependências Python necessárias para o projeto, usadas por `pip` ou `uv` para instalação.


