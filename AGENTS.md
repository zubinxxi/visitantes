# Visitantes AMP

Dos proyectos independientes — **no monorepo**. Cada comando se ejecuta desde la carpeta del proyecto.

## Backend (`backend/`)

- **Framework:** FastAPI + SQLModel asíncrono (asyncmy) + MariaDB
- **Python:** 3.10+, venv en `.venv/` — `source .venv/bin/activate`
- **Config:** `.env` con variables obligatorias (Settings crashea si falta alguna)
- **Entrypoint:** `app.main:app`
- **Prefijo obligatorio:** `PYTHONPATH=.` para todos los comandos Python

```bash
# Servidor dev
PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Migraciones
PYTHONPATH=. alembic -c alembic.ini upgrade head
PYTHONPATH=. alembic -c alembic.ini revision -m "descripcion" --autogenerate
PYTHONPATH=. alembic -c alembic.ini downgrade -1
```

- **Auth:** JWT + bcrypt (rounds=12) + permisos vía `sec_groups_apps`
- **DI:** `SessionDep` con `Annotated[AsyncSession, Depends(get_session)]`
- **Fotos:** Se suben a `photos/visitors/` y se sirven como estáticos en `/photos/visitors`
- **CRUD mantenimiento:** Generados programáticamente en `app/main.py` con `MaintenanceCRUD` + permisos granulares por `app_name`
- **Test manual:** `python test_backend.py` o `python check_db.py` (requieren servidor corriendo)
- **Usuarios prueba:** `sysadmin`, `admindemo`, `usuariodemo` (pass: `123456`)

## Frontend (`frontend/`)

- **Stack:** Vue 3 (Composition API + `<script setup>`) + Vite + Pinia + Vue Router
- **Node:** `^20.19.0 || >=22.12.0`
- **UI:** Tailwind CSS v4 (`@tailwindcss/vite`) + daisyui + diseño TailAdmin
- **Alias:** `@/` → `src/`
- **Proxy dev:** `/api` y `/photos` → `http://localhost:8000`
- **Fuente:** Outfit (Google Fonts)

```bash
npm run dev        # servidor dev con proxy
npm run type-check # vue-tsc --build
npm run lint       # oxlint --fix → eslint --fix
npm run build      # type-check → vite build
npm run test:unit  # vitest (jsdom) — sin tests aún
```

- **Permisos en rutas:** Cada ruta tiene `meta.appName` y el guard `beforeEach` verifica `perms.hasAccess()` contra la store de permisos
- **UI:** Sidebar colapsable (90px / 290px), header sticky con breadcrumbs, tarjetas con borde gray-200

## Impresora de etiquetas

- Modelo: **JD 168BT/168** — térmica
- Recursos: https://jadens.com/pages/jd168-download-and-video
- Prototipos PHP en `etiquetas/`

## Skills del agente

Usar según corresponda: `vue-best-practices`, `fastapi`, `frontend-design`, `interface-design`, `error-handling-patterns`, `brainstorming`, `api-design-principles`, `systematic-debugging`
