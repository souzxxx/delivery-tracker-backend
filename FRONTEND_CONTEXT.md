# 🎯 Contexto para Frontend — Delivery Tracker

Cole este arquivo ao iniciar o projeto frontend para contextualizar o agente.

---

## 📌 Resumo do Projeto

Sistema de rastreamento de entregas com:
- Autenticação JWT (usuário comum + admin)
- CRUD de pedidos com timeline de eventos
- Rastreio público por código
- Integração com ViaCEP e Nominatim (coordenadas)

---

## 🔗 Backend API

**Base URL:** `http://127.0.0.1:8000/api/v1`

### Autenticação

```
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=email@example.com&password=senha123
```

**Response:**
```json
{ "access_token": "eyJ...", "token_type": "bearer" }
```

**Usar token:**
```
Authorization: Bearer eyJ...
```

### Admin padrão
- Email: `admin@delivery.com`
- Senha: `admin123`

---

## 📡 Endpoints Principais

### Auth
| Método | Rota | Body | Auth |
|--------|------|------|------|
| POST | `/auth/login` | `username`, `password` (form) | ❌ |

### Users
| Método | Rota | Auth |
|--------|------|------|
| POST | `/users` | ❌ (cadastro) |
| GET | `/users/me` | 🔐 |

### Orders
| Método | Rota | Auth |
|--------|------|------|
| POST | `/orders` | 🔐 |
| GET | `/orders` | 🔐 (meus pedidos) |
| GET | `/orders/all` | 🔐 Admin |
| GET | `/orders/all?status_filter=in_transit` | 🔐 Admin |
| GET | `/orders/{id}` | 🔐 Dono/Admin |
| PATCH | `/orders/{id}/status` | 🔐 Dono/Admin |

### Tracking (Público)
| Método | Rota | Auth |
|--------|------|------|
| GET | `/track/{tracking_code}` | ❌ |

---

## 📦 Criar Pedido

```json
POST /orders
{
  "origin_address": {
    "cep": "01310-100",
    "number": "1000",
    "complement": "Sala 1"
  },
  "destination_address": {
    "cep": "22041-080",
    "number": "500"
  }
}
```

**Response:**
```json
{
  "id": 1,
  "tracking_code": "DT-A1B2C3D4",
  "status": "created",
  "owner_id": 1,
  "origin_address": {
    "id": 1,
    "cep": "01310100",
    "street": "Avenida Paulista",
    "number": "1000",
    "complement": "Sala 1",
    "city": "São Paulo",
    "state": "SP",
    "latitude": -23.5505,
    "longitude": -46.6333
  },
  "destination_address": { ... },
  "created_at": "2025-12-12T14:00:00",
  "updated_at": "2025-12-12T14:00:00"
}
```

---

## 🔄 Status do Pedido

| Status | Label (para UI) |
|--------|-----------------|
| `created` | Pedido criado |
| `in_transit` | Saiu para entrega |
| `delivered` | Entregue |
| `canceled` | Cancelado |

**Atualizar:**
```json
PATCH /orders/1/status
{ "status": "in_transit" }
```

---

## 📍 Rastreio Público (Timeline)

```
GET /track/DT-A1B2C3D4
```

```json
{
  "tracking_code": "DT-A1B2C3D4",
  "status": "in_transit",
  "status_label": "Saiu para entrega",
  "origin": { "city": "São Paulo", "state": "SP" },
  "destination": { "city": "Rio de Janeiro", "state": "RJ" },
  "events": [
    {
      "status": "in_transit",
      "status_label": "Saiu para entrega",
      "description": "Pedido coletado e saiu para entrega",
      "created_at": "2025-12-12T15:30:00"
    },
    {
      "status": "created",
      "status_label": "Pedido criado",
      "description": "Pedido registrado no sistema",
      "created_at": "2025-12-12T14:00:00"
    }
  ],
  "created_at": "2025-12-12T14:00:00",
  "updated_at": "2025-12-12T15:30:00"
}
```

---

## 👤 Roles

| Role | Permissões |
|------|------------|
| `user` | CRUD próprios pedidos |
| `admin` | Tudo + ver/editar qualquer pedido |

---

## 🎨 Telas Sugeridas

### Públicas (sem login)
1. **Login** — `/login`
2. **Cadastro** — `/register`
3. **Rastreio** — `/track` ou `/track/{code}` (input para código)

### Usuário logado
4. **Meus Pedidos** — `/orders` (lista)
5. **Criar Pedido** — `/orders/new` (form com CEP + número)
6. **Detalhes do Pedido** — `/orders/{id}` (timeline visual)

### Admin
7. **Dashboard** — `/admin` (todos pedidos + filtros)
8. **Gerenciar Usuários** — `/admin/users` (promover/rebaixar)

---

## 🛠️ Stack Sugerida (Frontend)

- **React 18+** (Vite)
- **TypeScript**
- **TailwindCSS** ou **Chakra UI**
- **React Router**
- **Axios** ou **fetch** para API
- **React Query** (opcional, para cache)
- **Zustand** ou **Context** para estado global (auth)

---

## 📋 Checklist Frontend

- [ ] Setup projeto (Vite + React + TS)
- [ ] Configurar TailwindCSS
- [ ] Criar contexto de autenticação
- [ ] Tela de Login
- [ ] Tela de Cadastro
- [ ] Tela de Rastreio (pública)
- [ ] Tela de Meus Pedidos
- [ ] Tela de Criar Pedido
- [ ] Tela de Detalhes (timeline)
- [ ] Dashboard Admin
- [ ] Responsividade mobile

---

## 🔧 Como rodar o backend

```bash
cd delivery-tracker-backend
source env/bin/activate
uvicorn app.main:app --reload
```

API disponível em: `http://127.0.0.1:8000`
Swagger: `http://127.0.0.1:8000/docs`

