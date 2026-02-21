# Hi Interview - Architecture Discovery

## Stack Confirmation
Yes. This repository is a **FastAPI + SQLAlchemy + Next.js (React)** stack.

Evidence:
- Backend dependencies include `fastapi`, `sqlalchemy`, `alembic`, `pytest`, `uvicorn` in `backend/pyproject.toml`.
- Backend runtime bootstrapped via Poetry script (`dev = "server.dev:main"`) in `backend/pyproject.toml`.
- DB migrations via Alembic in `backend/alembic.ini` and `backend/db/versions/920ec93bbdae_initial.py`.
- DB container via Docker Compose in `backend/docker-compose.yml`.
- Frontend dependencies include `next`, `react`, `react-dom`, `axios`; scripts are Next scripts in `frontend/package.json`.
- Styling uses SCSS modules (`*.module.scss`) and `sass` in `frontend/package.json`.
- Frontend package manager lock file is `frontend/yarn.lock`.

---

## Phase 1 - Backend Architecture Discovery

### 1) Framework and backend entrypoint
- Framework: **FastAPI**
- App creation file: `backend/server/routes/app.py`
- Dev entrypoint (uvicorn launcher): `backend/server/dev.py`

`backend/server/routes/app.py`:
```python
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.business.auth.auth_verifier import AuthVerifier
from server.routes.routes import get_all_routes
from server.shared.config import Config, Env
from server.shared.databasemanager import DatabaseManager

load_dotenv()

config = Config.from_env()
database = DatabaseManager.from_url(config.database_url)
auth_verifier = AuthVerifier(config)

app = FastAPI(
    title="Hi Interview",
    docs_url=None if config.env == Env.PROD else "/docs",
    redoc_url=None if config.env == Env.PROD else "/redoc",
    openapi_url=None if config.env == Env.PROD else "/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(get_all_routes(config, database, auth_verifier))
```

### 2) Route structure and client routes
- Routes are organized as route modules with `get_router(...)` factories:
  - `backend/server/routes/ping.py`
  - `backend/server/routes/auth.py`
  - `backend/server/routes/client.py`
- All mounted in `backend/server/routes/routes.py`.
- DB session is passed via `DatabaseManager` object and opened per-route with context manager.
- Auth dependency injection is custom via `auth_verifier.UserTokenInfo()`.
- Responses are serialized through immutable Pydantic models in `server/shared/pydantic.py`.

Full route file: `backend/server/routes/client.py`
```python
from fastapi import APIRouter

from server.business.auth.auth_verifier import AuthVerifier
from server.business.auth.schema import UserTokenInfo
from server.business.client.list import list_clients
from server.business.client.schema import PClient
from server.shared.databasemanager import DatabaseManager
from server.shared.pydantic import PList


def get_router(database: DatabaseManager, auth_verifier: AuthVerifier) -> APIRouter:
    router = APIRouter()

    @router.get("/client")
    async def list_clients_route(
        _: UserTokenInfo = auth_verifier.UserTokenInfo(),
    ) -> PList[PClient]:
        with database.create_session() as session:
            clients = list_clients(session)
            return PList(data=clients)

    return router
```

### 3) ORM pattern (Client model)
- ORM: SQLAlchemy 2.0 typed declarative (`Mapped`, `mapped_column`).
- Base class: `server.data.models.base.Base` extending `DeclarativeBase`.
- IDs: string UUIDs (`default=lambda: str(uuid.uuid4())`), not int autoincrement.
- Timestamps: `created_at` and `updated_at` with `server_default=func.now()`, plus `onupdate=func.now()` for `updated_at`.
- Relationships: explicit relationship to `User` via `assigned_user_id` foreign key.
- Column style: snake_case; unique constraint on `email`; no explicit indices declared in model/migration.

Full model: `backend/server/data/models/client.py`
```python
from typing import TYPE_CHECKING
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from server.data.models.base import Base

if TYPE_CHECKING:
    from server.data.models.user import User


class Client(Base):
    __tablename__ = "client"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    assigned_user_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("user.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    assigned_user: Mapped["User | None"] = relationship(
        "User", foreign_keys=[assigned_user_id]
    )
```

### 4) Pydantic schemas/serializers for Client
Yes.
- Schema file: `backend/server/business/client/schema.py`
- Uses project `BaseModel` (`from_attributes=True`, immutable/frozen) from `backend/server/shared/pydantic.py`

`backend/server/business/client/schema.py`:
```python
from datetime import datetime

from server.shared.pydantic import BaseModel


class PClient(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    assigned_user_id: str | None
    created_at: datetime
    updated_at: datetime
```

### 5) DB session injection style
They **do not** use `Depends(get_db)`.

Pattern used:
- A `DatabaseManager` instance is created at startup.
- Router factory gets `database: DatabaseManager`.
- Endpoint opens session inline:
  - `with database.create_session() as session:`

`backend/server/shared/databasemanager.py`:
```python
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker


class DatabaseManager:
    engine: Engine

    def __init__(self, engine: Engine):
        self.engine = engine
        self.session_factory = sessionmaker(bind=engine)

    def create_session(self) -> Session:
        return self.session_factory()

    @classmethod
    def from_url(cls, url: str) -> "DatabaseManager":
        return cls(create_engine(url))
```

### 6) Backend tests style (sample)
- Testing framework: `pytest`
- API tests use `fastapi.testclient.TestClient`.
- DB setup uses alembic migration + schema reset in `backend/test/conftest.py`.
- Fixtures create authenticated and unauthenticated clients.
- Test data created directly with ORM model instances.
- No factory library pattern observed.

Sample full file: `backend/test/routes/test_client.py`
```python
from fastapi.testclient import TestClient

from server.data.models.client import Client
from server.shared.databasemanager import DatabaseManager


def test_list_clients(test_client: TestClient, database: DatabaseManager) -> None:
    with database.create_session() as session:
        session.add(Client(email="alice@example.com", first_name="Alice", last_name="Smith"))
        session.add(Client(email="bob@example.com", first_name="Bob", last_name="Jones"))
        session.commit()

    response = test_client.get("/client")
    assert response.status_code == 200

    data = response.json()
    assert len(data["data"]) >= 2

    emails = [c["email"] for c in data["data"]]
    assert "alice@example.com" in emails
    assert "bob@example.com" in emails


def test_list_clients_unauthenticated(unauthenticated_test_client: TestClient) -> None:
    response = unauthenticated_test_client.get("/client")
    assert response.status_code == 401


def test_list_clients_with_assigned_user(
    test_client: TestClient, database: DatabaseManager, user_id: str
) -> None:
    with database.create_session() as session:
        session.add(
            Client(
                email="assigned@example.com",
                first_name="Charlie",
                last_name="Brown",
                assigned_user_id=user_id,
            )
        )
        session.commit()

    response = test_client.get("/client")
    assert response.status_code == 200

    data = response.json()
    assigned = [c for c in data["data"] if c["email"] == "assigned@example.com"]
    assert len(assigned) == 1
    assert assigned[0]["assigned_user_id"] == user_id
```

---

## Phase 2 - Frontend Discovery

### 7) Frontend framework
- Framework: **Next.js App Router (React)**
- `frontend/package.json` dependencies prove Next + React.

`frontend/package.json`:
```json
{
  "name": "frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "eslint"
  },
  "dependencies": {
    "@mantine/core": "^8.3.14",
    "@mantine/hooks": "^8.3.14",
    "@tabler/icons-react": "^3.36.1",
    "axios": "^1.13.5",
    "next": "16.1.6",
    "react": "19.2.3",
    "react-dom": "19.2.3"
  },
  "devDependencies": {
    "@eslint/eslintrc": "^3.3.3",
    "@types/node": "^20",
    "@types/react": "^19",
    "@types/react-dom": "^19",
    "eslint": "^9",
    "eslint-config-next": "15.3.4",
    "eslint-plugin-import": "^2.32.0",
    "postcss-preset-mantine": "^1.18.0",
    "postcss-simple-vars": "^7.0.1",
    "sass": "^1.97.3",
    "typescript": "^5"
  }
}
```

### 8) API call structure (clients list)
- Uses **axios** with a custom API class wrapper (`frontend/src/api/Api.ts`) and domain client wrapper (`frontend/src/api/clients.ts`).
- No React Query/SWR.
- Page fetches in `useEffect` and stores local state.

Client list component: `frontend/src/app/(authed)/clients/page.tsx`
```tsx
"use client";

import { Table, Title } from "@mantine/core";
import { useEffect, useState } from "react";

import { useApi } from "@/api/context";
import { Client } from "@/types/clients";

import styles from "./page.module.scss";

export default function ClientsPage() {
    const api = useApi();
    const [clients, setClients] = useState<Client[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        api.clients.listClients()
            .then(setClients)
            .finally(() => setLoading(false));
    }, [api]);

    if (loading) {
        return <div className={styles.container}>Loading...</div>;
    }

    return (
        <div className={styles.container}>
            <Title
                order={2}
                className={styles.title}
            >
                Clients
            </Title>
            <Table
                striped
                highlightOnHover
                withTableBorder
                withColumnBorders
            >
                <Table.Thead>
                    <Table.Tr>
                        <Table.Th>Name</Table.Th>
                        <Table.Th>Email</Table.Th>
                        <Table.Th>Assigned</Table.Th>
                    </Table.Tr>
                </Table.Thead>
                <Table.Tbody>
                    {clients.map(client => (
                        <Table.Tr key={client.id}>
                            <Table.Td>{client.first_name} {client.last_name}</Table.Td>
                            <Table.Td>{client.email}</Table.Td>
                            <Table.Td>{client.assigned_user_id ? "Yes" : "No"}</Table.Td>
                        </Table.Tr>
                    ))}
                </Table.Tbody>
            </Table>
        </div>
    );
}
```

### 9) Frontend routing structure
- Uses Next.js **App Router** filesystem routing under `frontend/src/app/`.
- Public route: `/login` via `frontend/src/app/login/page.tsx`.
- Protected grouping: `frontend/src/app/(authed)/...`.
- Client list route: `/clients` via `frontend/src/app/(authed)/clients/page.tsx`.
- Shared auth gate/navigation wrapper: `frontend/src/app/(authed)/layout.tsx` + `NavigationMenu.tsx`.

### 10) Styling conventions (`.module.scss`)
- CSS modules with kebab-case class names in several places (e.g., `nav-bar`, `nav-button-selected`).
- Also simple camel-ish names appear (`container`, `title`) depending on component.
- Nesting used for child selectors and pseudo-classes (`svg`, `&:hover`).
- Styling is utility-light; mostly local class names and Mantine CSS variables.

Example: `frontend/src/app/(authed)/components/NavigationMenu.module.scss`
```scss
.root {
    height: 100%;
}

.nav-bar {
    background-color: var(--mantine-color-black);
}

.nav-button {
    display: flex;
    align-items: center;
    margin: 10px 10px;
    height: 50px;
    border-radius: 5px;
    cursor: pointer;
    color: var(--mantine-color-gray-5);

    svg {
        margin: 0 8px;
    }

    &:hover {
        color: var(--mantine-color-white);
        background-color: var(--mantine-color-dark-4);
    }
}

.nav-button-selected {
    color: var(--mantine-color-white);
    background-color: var(--mantine-color-dark-3);
}

.main {
    background-color: var(--mantine-color-white);
    display: flex;
    flex-direction: column;
    height: 100%;
}

.loading {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
}
```

---

## Phase 3 - Architectural Understanding

- Service layer: **Light service/use-case layer exists** (`server/business/*`, e.g. `business/client/list.py`).
- Repository pattern: **No dedicated repository layer** found.
- Business logic location: split, but relatively thin; route handlers still manage session scope and some logic; auth login has query + password verification directly in route.
- Schema separation: **Yes**. ORM models under `server/data/models`, response/request contracts under `server/business/*/schema.py`.
- Async endpoints: Route handlers are `async def`, but DB access is synchronous SQLAlchemy sessions (no async engine/session).

---

## Additional production-readiness observations

- Type hints: broadly present in backend and frontend.
- Function docs: minimal; mostly self-explanatory code without docstrings.
- Linting/formatting:
  - Backend: Ruff configured in `backend/pyproject.toml`.
  - Frontend: ESLint + `eslint-config-next` in `frontend/package.json` / `frontend/eslint.config.mjs`.
- Migration naming:
  - Current migration file is `920ec93bbdae_initial.py` (revision hash + short name).
- Primary keys:
  - UUID string PKs for both `User` and `Client`.
- Soft delete:
  - Not implemented (no `deleted_at`/`is_deleted` fields or related query filters).

---

## Requested "first action" file set (quick index)

- Backend entry file: `backend/server/routes/app.py`
- Client model: `backend/server/data/models/client.py`
- Existing route file: `backend/server/routes/client.py`
- Existing test file: `backend/test/routes/test_client.py`
- Frontend package manifest: `frontend/package.json`
- Client list component: `frontend/src/app/(authed)/clients/page.tsx`

All are included above verbatim.
