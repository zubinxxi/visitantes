# VisitantesDB — Frontend

Aplicación web de gestión de visitantes para la Autoridad de los Asuntos de Indígenas (AAPI). Desarrollada con **Vue 3**, **Vite**, **TypeScript**, **Pinia** y **Tailwind CSS**. Diseño basado en la plantilla **TailAdmin Vue**.

## Tecnologías

| Categoría | Paquete | Versión |
| :--- | :--- | :--- |
| Framework | Vue 3 (Composition API + `<script setup>`) | ^3.5.x |
| Build Tool | Vite | ^8.x |
| Lenguaje | TypeScript | ^5.x |
| Estado | Pinia | ^3.x |
| Rutas | Vue Router | ^4.x |
| HTTP | Axios | ^1.x |
| UI | Tailwind CSS 4 (tema personalizado) | ^4.x |
| QR Scanner | html5-qrcode | ^2.x |
| Fuente | Outfit (Google Fonts) | — |
| Linting | oxlint + ESLint | — |
| Testing | Vitest | — |

## Estilo visual

El frontend utiliza el mismo sistema de diseño que **TailAdmin Vue**:

- **Color primario**: `brand-500` (#465fff)
- **Escala de grises**: gray-25 → gray-950
- **Tipografía**: Outfit (Google Fonts)
- **Sidebar**: blanco con borde derecho, colapsable (90px / 290px)
- **Header**: blanco sticky con breadcrumbs y notificaciones
- **Tarjetas**: fondo blanco, borde gray-200, sombra sutil
- **Tablas**: header con fondo gray-50, texto uppercase gray-400
- **Formularios**: inputs h-11, bordes gray-300, focus ring brand-500
- **Botones**: brand-500 con sombra, bordes redondeados lg

## Requisitos

- Node.js `^20.19.0` o `>=22.12.0`
- Backend corriendo en `http://localhost:8000`

## Instalación

```sh
npm install
```

## Desarrollo

```sh
npm run dev
```

El servidor de desarrollo escucha en `http://localhost:5173` y hace proxy de `/api` al backend en `localhost:8000`.

## Producción

```sh
npm run build
```

Los archivos compilados se generan en `dist/`, listos para servir con un servidor estático.

## Scripts disponibles

| Comando | Descripción |
| :--- | :--- |
| `npm run dev` | Servidor de desarrollo con hot-reload |
| `npm run build` | Type-check + compilación para producción |
| `npm run preview` | Vista previa del build de producción |
| `npm run test:unit` | Ejecutar pruebas unitarias con Vitest |
| `npm run lint` | Linting con oxlint + ESLint |

## Estructura del proyecto

```
src/
├── assets/
│   └── main.css          # Tailwind + tema TailAdmin (colores, sombras, utilities)
├── components/           # Componentes reutilizables
├── lib/
│   └── api.ts            # Cliente Axios (interceptores, auth, 401 handler)
├── router/
│   └── index.ts          # Rutas + guards de autenticación
├── stores/
│   └── auth.ts           # Pinia: login, logout, sesión persistente
├── types/
│   └── visit.ts          # Interfaces: Visit, Visitor, VisitStats
├── views/                # Páginas de la aplicación
│   ├── LoginView.vue           # Login split-layout (TailAdmin Signin style)
│   ├── LayoutView.vue          # Sidebar colapsable + header sticky
│   ├── DashboardView.vue       # Tarjetas estadísticas + tabla + acciones rápidas
│   ├── CheckInView.vue         # QR Scanner + formulario (panel dual)
│   ├── ActiveVisitsView.vue    # Tabla de visitas activas con checkout
│   └── VisitorsView.vue        # Búsqueda, listado y modal de detalles
├── App.vue
└── main.ts
```

## Rutas de la aplicación

| Ruta | Nombre | Descripción | Autenticado |
| :--- | :--- | :--- | :--- |
| `/login` | login | Inicio de sesión (split layout) | ❌ |
| `/` | dashboard | Panel con estadísticas y accesos rápidos | ✅ |
| `/checkin` | checkin | QR Scanner + formulario de registro | ✅ |
| `/active` | active | Tabla de visitas activas con checkout | ✅ |
| `/visitors` | visitors | Búsqueda, listado y detalles de visitantes | ✅ |

## Credenciales de prueba

| Usuario | Contraseña |
| :--- | :--- |
| sysadmin | 123456 |
| admindemo | 123456 |
| usuariodemo | 123456 |

## IDE recomendado

[Visual Studio Code](https://code.visualstudio.com/) + extensión [Vue - Official](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (deshabilitar Vetur si está instalada).

### Extensiones de navegador

- [Vue.js devtools](https://chromewebstore.google.com/detail/vuejs-devtools/nhdogjmejiglipccpnnnanhbledajbpd) para depuración en desarrollo.
