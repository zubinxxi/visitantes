# Análisis: Impresora de etiquetas a color EPSON ColorWorks CW-C6000A (C11CH76101)

## 1. ¿Es viable utilizar la impresora EPSON ColorWorks CW-C6000A?

**Sí, técnicamente es viable**, con las siguientes consideraciones:

- **Es una impresora de inyección de tinta (CMYK) diseñada para etiquetas a color.** A diferencia de la impresora térmica actual JD 168BT (que solo imprime en negro), la CW-C6000A sí imprime a todo color.
- **El flujo de impresión no cambia.** Las etiquetas se generan como documento (PDF en el prototipo PHP con html2pdf, o HTML en el componente Vue) y se envían al diálogo de impresión del navegador (`print(true)` / `window.print()`). Solo es necesario instalar el driver e seleccionar la CW-C6000A en dicho diálogo.
- **El color negro actual NO es una limitación de la impresora**, sino del código: las celdas de edificios visitados se pintan con `background-color:black` / `#000`. La CW-C6000A imprime cualquier color definido en el CSS/PDF.
- **Tamaños de etiqueta:** la CW-C6000A admite rollos de hasta ~104 mm de ancho. Las etiquetas actuales miden entre 76 mm y 101,6 mm de ancho → dentro del rango soportado.
- **Driver Linux (Debian 13):** el sistema ya cuenta con el paquete `printer-driver-escpr` (v1.7.17). Se debe verificar en el equipo físico que el modelo CW-C6000A esté incluido en el soporte ESC/P-R (los PPD se descargan dinámicamente), o configurar la impresora por IPP / driverless en CUPS. La conexión puede ser por USB o Ethernet.
- **Consumibles y medio:** requiere tintas pigmentadas CMYK y **etiquetas aptas para inyección de tinta** (el papel térmico actual no es compatible con esta impresora).

## 2. ¿Se puede hacer el cambio en el código para pintar cada cuadrante con el color del edificio?

**Sí, y es un cambio mínimo.** Dato clave: **el color de cada edificio ya existe en la base de datos**, en la tabla `building`, columna `code` (almacenado como HEX):

| ID | Edificio | Color (`code`) |
|----|----------|----------------|
| 1 | Edificio Uno | `#f95959` |
| 2 | Edificio Dos | `#3a9679` |
| 3 | Edificio Tres | `#c50d66` |
| 4 | Edificio Cuatro | `#4b0082` |
| 5 | Edificio Cinco | `#fabc60` |
| 6 | Edificio Seis | `#118df0` |
| 7 | PANCANAL (columna "P") | `#000000` (negro) |

**Dato requerido (PANCANAL):** el valor de color en `building.code` para el edificio 7 actualmente es `#1b262c` (azul muy oscuro, casi negro). Por indicación del usuario, se debe actualizar el valor en la base de datos a **negro (`#000000`)** para que el frontend lo consuma de forma normal, sin lógica especial en el código:

```sql
UPDATE building SET code = '#000000' WHERE id = 7;
```

### 2.1 Alcance del cambio

**Alcance acordado: solo el frontend (Vue).** Las etiquetas existen en dos implementaciones:

1. Prototipos PHP (`etiquetas/etiqueta_*.php`) — usados en producción ScriptCase.
2. Componente Vue (`frontend/src/components/VisitorBadge.vue`) — del nuevo frontend.

El cambio se aplica **únicamente al componente Vue** (`VisitorBadge.vue`). No requiere migraciones de base de datos ni cambios en backend, porque el color ya está en la tabla `building`.

### 2.2 Cambios en `frontend/src/components/VisitorBadge.vue`

1. **Importar el cliente API** (`import api from '@/lib/api'`), siguiendo el patrón del resto de componentes.
2. **Datos de color a nivel de módulo (compartidos entre instancias del badge):**
   - `const buildingColors = ref<Record<number, string>>({})` a nivel de módulo, de modo que los múltiples badges de la vista previa de impresión compartan una única carga.
3. **Función `loadBuildingColors()`** (llamada en `onMounted`): realiza `GET /maintenance/buildings/?limit=100` y construye el mapa directo `id → code` (consumiendo el valor HEX tal cual está en la tabla `building`, incluido `#000000` para PANCANAL). Si la llamada falla, el mapa queda vacío y se conserva el color negro actual como fallback (sin regresión).
4. **Helper `buildingColorFor(colIndex)`:** devuelve el HEX del edificio correspondiente a esa columna (mismo mapeo que el actual `isBuildingSelected`: columna 6 → id 7), o `#000` si no hay color.
5. **Actualizar las 4 plantillas del componente** (4x3, 3x4, 2x4, 4x2) sustituyendo:
   ```js
   backgroundColor: isBuildingSelected(idx) ? buildingColorFor(idx) : '#fff'
   ```

### 2.3 Verificación

- Ejecutar `npm run type-check` y `npm run lint` dentro de la carpeta `frontend/`.
- Si el endpoint devuelve `code`, conviene añadir `code?: string` a las interfaces locales `Building` (`CheckInView.vue` y `ActiveVisitsView.vue`) para un tipado correcto.

## 3. Notas de despliegue (infraestructura, no código)

- La CW-C6000A se imprime seleccionándola como impresora en el diálogo de impresión del navegador.
- Si la conexión es por red (Ethernet/IPP), abrir el puerto **631** en `ufw`. Si es USB directo, no se requiere apertura de puertos.
- Verificar en el equipo físico que el modelo CW-C6000A está soportado por el driver ESC/P-R instalado (`printer-driver-escpr`).
- Sustituir el medio: usar etiquetas aptas para inyección de tinta (el papel térmico actual no sirve).
