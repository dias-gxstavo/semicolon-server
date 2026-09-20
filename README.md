# semicolon - markdown editor

Backend de um editor simples de Markdown. O semicolon permite criar,
listar, consultar, editar e excluir notas, mantendo o conteúdo em texto
Markdown e os dados persistidos em SQLite.

## Tecnologias

- Python 3.14+.
- FastAPI para rotas HTTP e documentação OpenAPI.
- SQLAlchemy 2 para modelos, consultas e sessões de banco de dados.
- SQLite na configuração de exemplo e Alembic para migrações.
- Pydantic e pydantic-settings para schemas e configuração por ambiente.
- Loguru para logs; uv, Taskipy, Ruff e pre-commit para desenvolvimento.

## Executar localmente

Pré-requisitos: Python 3.14+ e uv disponíveis. Execute os comandos na raiz
do repositório para que a aplicação encontre o `.env` e o banco local.

```sh
uv sync
cp .env.example .env
uv run task server
```

O servidor de desenvolvimento fica em `http://127.0.0.1:8000`.

- Swagger UI: `http://127.0.0.1:8000/docs`.
- Verificação do banco: `http://127.0.0.1:8000/health`.

## Modelo de nota

| Campo | Tipo | Comportamento |
| --- | --- | --- |
| `note_id` | inteiro | Chave primária gerada pelo banco. |
| `title` | texto | Obrigatório e único no banco. |
| `content` | texto | Conteúdo Markdown, armazenado sem renderização. |
| `created_at` | data e hora | Preenchido pelo banco na criação. |
| `updated_at` | data e hora | Preenchido na criação e atualizado pelo ORM nas alterações. |

A listagem omite `content` para evitar carregar o corpo de todas as notas.
A consulta individual, a criação e a edição retornam a nota completa.

## API

| Método | Rota | Resultado de sucesso |
| --- | --- | --- |
| `GET` | `/health` | `200`: estado da conexão com o banco. |
| `POST` | `/notes/` | `201`: cria uma nota com `title` e `content`. |
| `GET` | `/notes/?skip=0&limit=10` | `200`: lista os metadados das notas. |
| `GET` | `/notes/{note_id}` | `200`: retorna uma nota com seu conteúdo. |
| `PATCH` | `/notes/{note_id}` | `200`: altera apenas os campos enviados. |
| `DELETE` | `/notes/{note_id}` | `204`: exclui a nota, sem corpo de resposta. |


## Estrutura do projeto

```text
src/
├── main.py          # Aplicação, lifespan, CORS e health check
├── settings.py      # Leitura de DATABASE_URL e .env
├── database.py      # Engine, sessões e dependência get_db
├── models/note.py   # Modelo ORM e metadados das tabelas
├── schemas/note.py  # Contratos de entrada e saída
└── routers/notes.py # Operações HTTP sobre notas
migrations/         # Ambiente Alembic e revisões do schema
alembic.ini         # Configuração do Alembic
pyproject.toml      # Dependências e tarefas de desenvolvimento
uv.lock             # Versões resolvidas das dependências
```

## Desenvolvimento local

```sh
uv run task lint
uv run task format
uv run pre-commit install
```

O comando `format` modifica arquivos. Para apenas verificar a formatação,
use `uv run task lint`.
