# 📦 Delivery Tracker — Backend

Backend profissional para sistema de rastreamento de entregas, com autenticação JWT, banco PostgreSQL e integração com APIs de geolocalização.

## 🚀 Stack

- **Python 3.12** + **FastAPI**
- **PostgreSQL** (via Docker)
- **SQLAlchemy** (ORM)
- **JWT** (OAuth2 Password Flow)
- **bcrypt** (hash de senhas)
- **ViaCEP** (auto-preenchimento de endereço)
- **Nominatim/OSM** (geocodificação)

## 📁 Estrutura

```
app/
├── api/api_v1/
│   ├── endpoints/
│   │   ├── auth.py        # Login
│   │   ├── users.py       # CRUD usuários + promoção admin
│   │   ├── orders.py      # CRUD pedidos + rotas admin
│   │   ├── tracking.py    # Rastreio público
│   │   └── health.py      # Health check
│   └── api.py             # Router principal
├── models/
│   ├── user.py            # User + UserRole
│   ├── address.py         # Address
│   ├── order.py           # Order + OrderStatus
│   └── order_event.py     # OrderEvent (timeline)
├── schemas/               # Pydantic schemas
├── services/
│   ├── auth_service.py    # JWT + get_current_user/admin
│   ├── viacep_service.py  # Integração ViaCEP
│   └── geocoding_service.py # Integração Nominatim
└── core/config.py         # Settings (.env)
```

## ⚙️ Setup

### 1. Banco de dados (Docker)

```bash
docker run --name delivery-postgres \
  -e POSTGRES_USER=delivery_user \
  -e POSTGRES_PASSWORD=delivery_password \
  -e POSTGRES_DB=delivery_db \
  -p 5432:5432 \
  -v delivery_pg_data:/var/lib/postgresql/data \
  -d postgres:16
```

### 2. Ambiente virtual

```bash
python -m venv env
source env/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### 3. Variáveis de ambiente

```bash
cp .env.example .env
# Edite o .env com suas configurações
```

### 4. Criar tabelas

```bash
python create_tables.py
python create_admin.py  # Cria admin inicial
```

### 5. Rodar servidor

```bash
uvicorn app.main:app --reload
```

Acesse: http://127.0.0.1:8000/docs

---

## 🔐 Autenticação

### Roles
- `user` — Usuário comum (padrão)
- `admin` — Administrador

### Admin padrão
- Email: `admin@delivery.com`
- Senha: `admin123`

---

## 📡 API Endpoints

### Auth
| Método | Rota | Descrição | Auth |
|--------|------|-----------|------|
| POST | `/api/v1/auth/login` | Login (retorna JWT) | ❌ |

### Users
| Método | Rota | Descrição | Auth |
|--------|------|-----------|------|
| POST | `/api/v1/users` | Criar usuário | ❌ |
| GET | `/api/v1/users` | Listar todos | 🔐 Admin |
| GET | `/api/v1/users/me` | Meus dados | 🔐 |
| PUT | `/api/v1/users/{id}/role` | Promover/rebaixar | 🔐 Admin |

### Orders
| Método | Rota | Descrição | Auth |
|--------|------|-----------|------|
| POST | `/api/v1/orders` | Criar pedido | 🔐 |
| GET | `/api/v1/orders` | Meus pedidos | 🔐 |
| GET | `/api/v1/orders/all` | Todos pedidos | 🔐 Admin |
| GET | `/api/v1/orders/all?status_filter=in_transit` | Filtrar por status | 🔐 Admin |
| GET | `/api/v1/orders/{id}` | Detalhes | 🔐 Dono/Admin |
| PATCH | `/api/v1/orders/{id}/status` | Atualizar status | 🔐 Dono/Admin |

### Tracking (Público)
| Método | Rota | Descrição | Auth |
|--------|------|-----------|------|
| GET | `/api/v1/track/{tracking_code}` | Rastrear pedido | ❌ |

---

## 📦 Criar Pedido

**POST /api/v1/orders**

```json
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

> ✅ `street`, `city`, `state` são preenchidos automaticamente via **ViaCEP**
> ✅ `latitude`, `longitude` são preenchidos via **Nominatim**

**Response:**
```json
{
  "id": 1,
  "tracking_code": "DT-A1B2C3D4",
  "status": "created",
  "origin_address": {
    "cep": "01310100",
    "street": "Avenida Paulista",
    "number": "1000",
    "city": "São Paulo",
    "state": "SP",
    "latitude": -23.5505,
    "longitude": -46.6333
  },
  ...
}
```

---

## 🔄 Status do Pedido

| Status | Label | Descrição |
|--------|-------|-----------|
| `created` | Pedido criado | Registrado no sistema |
| `in_transit` | Saiu para entrega | Coletado pelo entregador |
| `delivered` | Entregue | Finalizado com sucesso |
| `canceled` | Cancelado | Cancelado |

**Atualizar status:**
```json
PATCH /api/v1/orders/1/status
{ "status": "in_transit" }
```

---

## 📍 Rastreio Público

**GET /api/v1/track/DT-A1B2C3D4**

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
  ]
}
```

---

## 🗃️ Modelos

### User
```
id, email, hashed_password, full_name, role
```

### Address
```
id, cep, street, number, complement, city, state, latitude, longitude
```

### Order
```
id, tracking_code, status, owner_id, origin_address_id, destination_address_id, created_at, updated_at
```

### OrderEvent
```
id, order_id, status, status_label, description, created_at
```

---

## 🧪 Testar

1. Acesse `/docs` (Swagger)
2. Clique em **Authorize**
3. Use `admin@delivery.com` / `admin123`
4. Teste as rotas!

---

## 📄 Licença

MIT
