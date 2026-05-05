# AGENTS.md - Visitantes AMP

## Estructura
- `backend/` — FastAPI + SQLModel (Python, .venv)
- `frontend/` — Vue 3 + Vite + Pinia + Tailwind (npm)

No es monorepo; cada carpeta es un proyecto independiente.

## Backend (FastAPI)
- Entorno: `backend/.venv` (Python 3.10+)
- Activar: `source .venv/bin/activate`
- Servidor: `PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
- Migraciones Alembic: `PYTHONPATH=. alembic -c alembic.ini upgrade head`
- Configuración en `.env` (basado en `.env.example`) — **nunca commitear**
- BD: MariaDB, base `visitorsdb`, credenciales en `.env`
- Entrypoint: `app/main.py` → `app.main:app`

## Frontend (Vue 3)
- Instalar: `cd frontend && npm install`
- Dev server: `npm run dev` (proxy `/api` → `http://localhost:8000`)
- Lint: `npm run lint` (oxlint primero, luego eslint)
- Build: `npm run build` (ejecuta type-check antes de vite build)
- Type check: `npm run type-check` (vue-tsc)
- Tests: `npm run test:unit` (vitest, jsdom)
- Alias `@/` → `frontend/src/`

## Convenciones del proyecto
- **Idioma:** Todo (código, comentarios, respuestas) en español
- **Vue:** Composition API + `<script setup>` obligatorio
- **UI:** Diseño basado en TailAdmin Vue + Tailwind CSS + daisyui
- **FastAPI:** Pydantic v2, tipado estático, `SessionDep` con `Annotated`
- **Auth:** JWT + permisos vía `sec_groups_apps`

## Fase actual
- Fase 4 (Impresión de etiquetas térmicas) pendiente
- Usuarios de prueba: `sysadmin`, `admindemo`, `usuariodemo` (pass: `123456`)

## Referencias
- `backend/README.md` — Documentación completa API
- `PLAN.md` — Fases y endpoints
- `instructions.md` — Reglas de desarrollo
- `correciones_y_reglas.txt` — Pendientes y correcciones
