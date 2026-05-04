# Reglas de Desarrollo - Proyecto Visitantes AMP

Este documento establece las normas estrictas de comportamiento para la generación de código y asistencia técnica.

## 1. Idioma de Interacción
- **Obligatorio:** Todas las explicaciones, comentarios de código, documentación y respuestas deben ser exclusivamente en **Español**.
- Si se detecta un término técnico sin traducción clara, se usará el término en inglés seguido de una breve explicación en español.

## 2. Fidelidad a la Documentación Oficial
El modelo DEBE regirse estrictamente por los estándares y mejores prácticas de las siguientes fuentes oficiales, evitando patrones obsoletos:

- **Backend (FastAPI):** Referenciar siempre [https://fastapi.tiangolo.com/es/](https://fastapi.tiangolo.com/es/). Priorizar el uso de Pydantic v2 y tipado estático (Type Hints).
- **Frontend (Vue.js 3):** Referenciar [https://vuejs.org/guide/quick-start.html](https://vuejs.org/guide/quick-start.html). Utilizar **Composition API** y la sintaxis `<script setup>`.
- **Diseño y UI (TailAdmin):** Seguir la estructura de componentes y clases de Tailwind CSS basadas en [https://vue-demo.tailadmin.com/], [https://vue-multiselect.js.org/], (https://vue-demo.tailadmin.com/), (https://vue-multiselect.js.org/).

## 3. Restricciones Técnicas del Entorno
- Sistema Operativo: **Debian 13**.
- Firewall: **ufw** activo (asegurar que los endpoints propuestos consideren la apertura de puertos si es necesario).
- Base de Datos: Considerar la integración con **MariaDB** según el histórico del sistema.