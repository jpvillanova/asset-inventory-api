# Asset Inventory API

API REST para **inventário de ativos de TI**, com autenticação **JWT**,
**controle de acesso por papel (RBAC)** e **histórico de postura de segurança**.
Construída com **FastAPI** e **SQLModel**, testada com **pytest** e pronta para
rodar em contêiner com **PostgreSQL**.

> Projeto de portfólio inspirado em uma atividade real de GRC/Segurança da
> Informação: manter um inventário de ativos confiável, com trilha de acesso,
> separação de responsabilidades e **avaliação contínua de segurança**.

## 🔗 Faz parte de um pipeline integrado

Esta API se integra ao projeto
[**security-headers-scanner**](https://github.com/jpvillanova/security-headers-scanner),
formando um fluxo de GRC ponta a ponta:

```
  ┌──────────────────────┐   1. lista ativos web    ┌──────────────────────────┐
  │  Asset Inventory API  │ ───────────────────────▶ │ security-headers-scanner │
  │  (FastAPI + Postgres) │                           │   (auditoria OWASP)      │
  │                       │ ◀─────────────────────── │                          │
  └──────────────────────┘   2. envia a postura      └──────────────────────────┘
         (POST /assets/{id}/scans — nota A–F e achados por ativo)
```

O inventário é a **fonte da verdade** dos ativos; o scanner audita os ativos web
e devolve a nota de segurança, que fica registrada como histórico.

## 🔑 Principais recursos

- **CRUD completo de ativos** (nome, categoria, nº de série, status, responsável, localização, URL).
- **Autenticação JWT** via OAuth2 *password flow*.
- **RBAC** com três papéis:
  | Papel | Permissões |
  |---|---|
  | `admin` | criar, editar e remover ativos; registrar varreduras |
  | `auditor` | **somente leitura** (auditoria / compliance) |
  | `user` | leitura e criação |
- **Histórico de varreduras de segurança** por ativo (`/assets/{id}/scans`).
- **Paginação e busca** por nome/categoria na listagem.
- **Exportação CSV** para relatórios de auditoria (`/assets/export`).
- Validação com Pydantic/SQLModel e **documentação OpenAPI/Swagger** automática.
- Senhas com hash (`pbkdf2_sha256`) e **testes de integração** (RBAC, CRUD, scans).

## 📚 Endpoints

| Método | Rota | Papel | Descrição |
|---|---|---|---|
| `POST` | `/auth/token` | público | Login, retorna JWT |
| `GET` | `/auth/me` | autenticado | Dados do usuário atual |
| `GET` | `/assets` | autenticado | Lista paginada (`?q=`, `?category=`, `?limit=`, `?offset=`) |
| `GET` | `/assets/export` | autenticado | Exporta todos os ativos em CSV |
| `GET` | `/assets/{id}` | autenticado | Detalhe do ativo |
| `POST` | `/assets` | admin | Cria ativo |
| `PUT` | `/assets/{id}` | admin | Atualiza (parcial) |
| `DELETE` | `/assets/{id}` | admin | Remove |
| `POST` | `/assets/{id}/scans` | admin | Registra uma varredura de segurança |
| `GET` | `/assets/{id}/scans` | autenticado | Histórico de varreduras |
| `GET` | `/assets/{id}/scans/latest` | autenticado | Última varredura |

## 🏗 Arquitetura

```
app/
├── main.py          # app FastAPI, lifespan (cria tabelas + semeia admin), /health
├── database.py      # engine e sessão (SQLite por padrão; PostgreSQL em produção)
├── models.py        # tabelas: User, Asset, SecurityScan + enums
├── schemas.py       # DTOs de entrada/saída
├── auth.py          # JWT, hash de senha e dependências de RBAC
├── crud.py          # acesso a dados (ativos, paginação, CSV, varreduras)
└── routers/
    ├── auth.py      # /auth/*
    ├── assets.py    # /assets (CRUD, busca, export)
    └── scans.py     # /assets/{id}/scans
scripts/seed_demo.py # popula ativos de exemplo
tests/               # pytest (auth, CRUD, RBAC, scans, paginação, CSV)
```

## 🚀 Como rodar

### Local (SQLite)

```sh
python -m venv .venv
# Windows: .venv\Scripts\activate | Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env            # opcional
uvicorn app.main:app --reload
python -m scripts.seed_demo     # (opcional) dados de exemplo
```

### Docker + PostgreSQL

```sh
docker compose up --build
```

- API: <http://127.0.0.1:8000> · Swagger: <http://127.0.0.1:8000/docs>

No primeiro boot é criado o usuário admin (`admin` / `admin123` por padrão —
troque em produção pelo `.env`).

## 🧪 Testes

```sh
pytest -v
```

Executados automaticamente no **GitHub Actions** (`.github/workflows/ci.yml`).

## 📡 Exemplo

```sh
# Token
curl -X POST http://127.0.0.1:8000/auth/token -d "username=admin&password=admin123"

# Criar um ativo web
curl -X POST http://127.0.0.1:8000/assets \
  -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" \
  -d '{"name":"Portal","category":"web","url":"https://example.com"}'

# Exportar inventário em CSV
curl http://127.0.0.1:8000/assets/export -H "Authorization: Bearer <TOKEN>"
```

## 🛠 Stack

`Python` · `FastAPI` · `SQLModel` · `Pydantic` · `JWT (PyJWT)` · `passlib` ·
`PostgreSQL` · `Docker` · `pytest` · `GitHub Actions`
