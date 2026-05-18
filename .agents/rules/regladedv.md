---
trigger: always_on
---

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

# Reglas de Desarrollo - Proyecto Visitantes AMP

Este documento establece las normas estrictas de comportamiento para la generación de código y asistencia técnica.

## 1. Idioma de Interacción

- **Obligatorio:** Todas las explicaciones, comentarios de código, documentación y respuestas deben ser exclusivamente en **Español**.
- Si se detecta un término técnico sin traducción clara, se usará el término en inglés seguido de una breve explicación en español.

## 2. Fidelidad a la Documentación Oficial

El modelo DEBE regirse estrictamente por los estándares y mejores prácticas de las siguientes fuentes oficiales, evitando patrones obsoletos:

- **Backend (FastAPI):** Referenciar siempre [https://fastapi.tiangolo.com/es/](https://fastapi.tiangolo.com/es/). Priorizar el uso de Pydantic v2 y tipado estático (Type Hints).
- **Frontend (Vue.js 3):** Referenciar [https://vuejs.org/guide/quick-start.html](https://vuejs.org/guide/quick-start.html). Utilizar **Composition API** y la sintaxis `<script setup>`. Utilizar **vue-multiselect** para todos los campos de selección (Única y Multiple) referenciar [https://vue-multiselect.js.org/](https://vue-multiselect.js.org/).

- **Diseño y UI (TailAdmin):** Seguir la estructura de componentes y clases de Tailwind CSS basadas en [https://vue-demo.tailadmin.com/](https://vue-demo.tailadmin.com/).

## 3. Restricciones Técnicas del Entorno

- Sistema Operativo: **Debian 13**.
- Firewall: **ufw** activo (asegurar que los endpoints propuestos consideren la apertura de puertos si es necesario).
- Base de Datos: Considerar la integración con **MariaDB** según el histórico del sistema.

## 4. Directrices de Modificación de Código

Estas directrices aplican a toda modificación de código, independientemente de la skill o tecnología involucrada.

### 4.1 Precisión Quirúrgica

- **Fidelidad al Alcance:** Modifica única y exclusivamente las líneas o funciones solicitadas.
- **Prohibición de Refactorización Silenciosa:** No cambies nombres de variables, estructuras de bases de datos o lógica circundante para "limpiar" el código, a menos que se pida explícitamente.
- **Preservación de Estilo:** Mantén el patrón de diseño y las convenciones de nomenclatura detectadas en el código existente (ej. CamelCase o snake_case, no los mezcles).

### 4.2 Integridad del Sistema

- **Respeto a la Arquitectura:** Antes de sugerir un cambio, analiza cómo afecta a los componentes dependientes (especialmente en entornos multi-tenant o arquitecturas de microservicios).
- **Consistencia de Datos:** Al proponer cambios en consultas SQL o esquemas, asegura la compatibilidad con los tipos de datos y relaciones existentes.
- **Comentarios de Cambio:** Si una modificación requiere ajustar una configuración en otro archivo (ej. variable de entorno o ruta), notifícalo al final de la respuesta.

### 4.3 Verificación y Comunicación

- **Confirmación de Ambigüedad:** Si una instrucción puede interpretarse de forma que rompa la compatibilidad hacia atrás, solicita aclaración antes de proceder.
- **Bloques Contextuales:** Devuelve suficiente código para entender dónde va el cambio, pero evita reescribir archivos masivos si la modificación es puntual.
- **Explicaciones Técnicas:** Proporciona una explicación breve de qué se cambió y por qué es seguro para el resto del sistema, solo si la lógica es compleja.

### 4.4 Control de Regresiones

- Antes de generar la respuesta final, verifica mentalmente que el nuevo código no altera funciones auxiliares ni dependencias compartidas.
