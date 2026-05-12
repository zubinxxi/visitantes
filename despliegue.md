# Guía de Despliegue - Visitantes AMP

Esta guía detalla los pasos para desplegar el proyecto en un servidor **Debian 13** utilizando **CloudPanel v2.5.3**.

## 1. Requisitos Previos en CloudPanel

1.  **Base de Datos**: 
    - Crea una base de datos MariaDB desde el panel.
    - Anota el nombre, usuario y contraseña.
2.  **Sitio para el Backend**:
    - Añadir sitio -> **Create a Python Site**.
    - Dominio: `api.tudominio.com` (Ejemplo).
    - Anota el **App Port** asignado (ej. `8080`).
3.  **Sitio para el Frontend**:
    - Añadir sitio -> **Create a Static Site**.
    - Dominio: `tudominio.com`.

---

## 2. Despliegue del Backend (FastAPI)

1.  **Subir archivos**: Sube el contenido de la carpeta `backend/` a `/home/cloudpanel-user/htdocs/api.tudominio.com/`.
2.  **Configurar Entorno**:
    ```bash
    cd /home/cloudpanel-user/htdocs/api.tudominio.com/
    # Instalar dependencias del sistema necesarias
    sudo apt update
    sudo apt install python3.13-venv python3.13-dev build-essential libmariadb-dev
    
    # Crear y activar entorno virtual
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```
3.  **Archivo .env**: Crea el archivo `.env` basado en `.env.example` con los datos reales de producción (DB_NAME, DB_USER, DB_PASS, SMTP, FRONTEND_HOST). 
    *Nota: El sistema soporta caracteres especiales en la contraseña de la base de datos.*
4.  **Migraciones de Base de Datos**: Sincroniza la estructura de la base de datos:
    ```bash
    PYTHONPATH=. alembic upgrade head
    ```
5.  **Servicio Systemd**: Crea el servicio para mantener el backend activo: `sudo nano /etc/systemd/system/visitantes-api.service`
    ```ini
    [Unit]
    Description=FastAPI Production Server
    After=network.target

    [Service]
    User=cloudpanel-user
    Group=cloudpanel-user
    WorkingDirectory=/home/cloudpanel-user/htdocs/api.tudominio.com
    Environment="PATH=/home/cloudpanel-user/htdocs/api.tudominio.com/.venv/bin"
    # Usamos fastapi run para producción en el puerto asignado por CloudPanel
    ExecStart=/home/cloudpanel-user/htdocs/api.tudominio.com/.venv/bin/fastapi run app/main.py --port 8080

    [Install]
    WantedBy=multi-user.target
    ```
6.  **Activar**:
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable --now visitantes-api
    ```

---

## 3. Despliegue del Frontend (Vue 3)

1.  **Configurar Entorno**: Crea un archivo `.env.production` en la carpeta `frontend/`:
    ```env
    VITE_API_URL=https://api.tudominio.com
    ```
2.  **Generar el Build** (Localmente o en servidor):
    ```bash
    cd frontend
    npm install --legacy-peer-deps
    npm run build
    ```
2.  **Subir archivos**: Sube el contenido de `frontend/dist/` a `/home/cloudpanel-user/htdocs/tudominio.com/`.
3.  **Configurar Nginx (SPA)**: En CloudPanel, ve a **Vhost** del sitio frontend y añade esta regla para permitir las rutas de Vue:
    ```nginx
    location / {
        try_files $uri $uri/ /index.html;
    }
    ```

---

## 4. Pasos Finales

1.  **SSL**: Activa **Let's Encrypt** en la pestaña SSL/TLS para ambos dominios.
2.  **CORS**: Verifica que `FRONTEND_HOST` en el `.env` del backend coincida con la URL de tu frontend.
3.  **Pruebas**: Accede a tu dominio y verifica el inicio de sesión.
