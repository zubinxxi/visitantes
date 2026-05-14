# Guía de Despliegue - Visitantes AMP

Esta guía detalla los pasos para desplegar el proyecto en un servidor **Debian 12/13** utilizando **CloudPanel v2.5.3**.

## 1. Requisitos Previos en CloudPanel

1.  **Base de Datos**: 
    - Crea una base de datos MariaDB desde el panel.
    - Anota el nombre, usuario y contraseña.
2.  **Sitio para el Backend**:
    - Añadir sitio -> **Create a Python Site**.
    - Dominio: `api.tudominio.com`.
    - Anota el **App Port** asignado (ej. `8080`).
3.  **Sitio para el Frontend**:
    - Añadir sitio -> **Create a Static Site**.
    - Dominio: `tudominio.com`.

---

## 2. Despliegue del Backend (FastAPI)

1.  **Subir archivos**: Sube el contenido de la carpeta `backend/` a `/home/usuario/htdocs/api.tudominio.com/`.
2.  **Configurar Entorno**:
    ```bash
    cd /home/usuario/htdocs/api.tudominio.com/
    sudo apt update
    sudo apt install python3.13-venv python3.13-dev build-essential libmariadb-dev
    
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```
3.  **Archivo .env**: Crea el archivo `.env` basado en `.env.example` con los datos reales:
    ```env
    DB_HOST=localhost
    DB_PORT=3306
    DB_NAME=visitorsdb
    DB_USER=visitorsdb
    DB_PASS=tu_password

    SECRET_KEY=tu_clave_secreta_segura
    ACCESS_TOKEN_EXPIRE_MINUTES=480

    DEBUG=false

    # URL del frontend (para CORS y enlaces en correos)
    FRONTEND_HOST=https://tudominio.com

    # SMTP (opcional, para recuperación de contraseña)
    SMTP_HOST=
    SMTP_PORT=587
    SMTP_USER=
    SMTP_PASSWORD=
    EMAILS_FROM_EMAIL=info@tudominio.com
    EMAILS_FROM_NAME=Visitantes
    ```
4.  **Migraciones**:
    ```bash
    source .venv/bin/activate
    PYTHONPATH=. alembic upgrade head
    ```
5.  **Servicio Systemd**:
    ```bash
    sudo nano /etc/systemd/system/visitantes-api.service
    ```
    ```ini
    [Unit]
    Description=FastAPI Production Server
    After=network.target

    [Service]
    User=usuario
    Group=usuario
    WorkingDirectory=/home/usuario/htdocs/api.tudominio.com
    Environment="PATH=/home/usuario/htdocs/api.tudominio.com/.venv/bin"
    ExecStart=/home/usuario/htdocs/api.tudominio.com/.venv/bin/fastapi run app/main.py --port 8000

    [Install]
    WantedBy=multi-user.target
    ```
    *CloudPanel crea un sitio Python con su propio puerto, pero puedes usar `8000` directamente para simplificar el proxy.*

6.  **Activar**:
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable --now visitantes-api
    ```

---

## 3. Despliegue del Frontend (Vue 3)

1.  **Generar el Build** (localmente o en servidor):
    ```bash
    cd frontend
    npm install
    npm run build
    ```
    *No necesita `.env.production` — el frontend usa rutas relativas (`/api/v1/...`).*

2.  **Subir archivos**: Sube el contenido de `frontend/dist/` a `/home/usuario/htdocs/tudominio.com/`.

3.  **Configurar Nginx (proxy reverso)**: En CloudPanel, ve a **Vhost** del sitio frontend y **reemplaza** todo el contenido con:

    ```nginx
    server {
      listen 80;
      listen [::]:80;
      listen 443 quic;
      listen 443 ssl;
      listen [::]:443 quic;
      listen [::]:443 ssl;
      http2 on;
      server_name tudominio.com;
      root /home/usuario/htdocs/tudominio.com;

      access_log /home/usuario/logs/nginx/access.log main;
      error_log /home/usuario/logs/nginx/error.log;

      include /etc/nginx/global_settings;
      add_header Cache-Control no-transform;

      index index.html;

      # Proxy al backend (FastAPI)
      location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_connect_timeout 900;
        proxy_send_timeout 900;
        proxy_read_timeout 900;
      }

      # Proxy de fotos (usa ^~ para prioridad sobre bloques regex)
      location ^~ /photos/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
      }

      # SPA: todas las rutas al index.html
      location / {
        try_files $uri $uri/ /index.html;
      }

      # Archivos estáticos con cache
      location ~* ^.+\.(css|js|jpg|jpeg|gif|png|ico|gz|svg|svgz|ttf|otf|woff|woff2|eot|mp4|ogg|ogv|webm|webp|zip|swf)$ {
        add_header Access-Control-Allow-Origin "*";
        expires max;
        access_log off;
      }

      location ~ /.well-known {
        auth_basic off;
        allow all;
      }
    }
    ```

    > **Importante:** El location `^~ /photos/` debe ir **antes** del bloque regex de archivos estáticos para que las fotos servidas por el backend no sean interceptadas. Sin el `^~`, nginx da prioridad al regex `.jpg` e intenta servir las fotos desde el `root` del frontend, resultando en 404.

---

## 4. Pasos Finales

1.  **SSL**: Activa **Let's Encrypt** en la pestaña SSL/TLS del sitio frontend.
2.  **CORS**: Verifica que `FRONTEND_HOST` en el `.env` del backend esté correcto (debe ser `https://tudominio.com`).
3.  **Service**: Asegúrate de que el servicio del backend esté activo:
    ```bash
    sudo systemctl status visitantes-api
    curl http://127.0.0.1:8000/api/v1/health
    ```
    Debe responder `{"status":"ok","db":"visitorsdb"}`.
4.  **Pruebas**: Accede a `https://tudominio.com` y verifica login, fotos y operaciones.

---

## 5. Notas Importantes

- **Fotos**: Se almacenan en `backend/photos/visitors/`. El proxy de nginx las sirve desde el backend a través de `^~ /photos/`.
- **VITE_API_URL**: Ya no se usa. El frontend siempre hace peticiones relativas al mismo origen, y nginx se encarga del proxy al backend.
- **api.tudominio.com**: El sitio del backend puede seguir existiendo para acceder directamente a la documentación OpenAPI (`/docs`), pero no es necesario para el funcionamiento normal.
