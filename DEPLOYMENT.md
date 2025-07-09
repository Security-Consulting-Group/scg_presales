# Digital Ocean Deployment Guide - WORKING VERSION

## Prerequisites

- Digital Ocean Droplet (Ubuntu 20.04 LTS or 22.04 LTS recommended)
- PostgreSQL Database on Digital Ocean
- Domain name (securitygroupcr.com) pointing to your droplet's IP
- SSH access to your droplet

## Step 1: Initial Server Setup

### 1. Connect to your droplet:
```bash
ssh root@your-droplet-ip
```

### 2. Update the system:
```bash
apt update && apt upgrade -y
```

### 3. Install Docker and Docker Compose:
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose-plugin -y

# Start Docker service
systemctl enable docker
systemctl start docker
```

### 4. Install Git:
```bash
apt install git -y
```

## Step 2: Clone and Setup Project

### 1. Clone your repository:
```bash
git clone <your-repository-url>
cd scg_presales
```

### 2. Create the production environment file:
```bash
mkdir -p env_config
nano env_config/production.env
```

### 3. Configure your production environment variables:
```bash
# Django Settings
SECRET_KEY_PROD=your-very-secret-key-here
DEBUG=False
ALLOWED_HOSTS=securitygroupcr.com,www.securitygroupcr.com

# Database Settings (Digital Ocean Database)
DB_NAME=DB_SCG_PRESALES_PROD
DB_USER=SCG_PRESALES_USER
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=25060

# Email Settings (Microsoft 365)
EMAIL_HOST=smtp.office365.com
EMAIL_HOST_USER=your-email@securitygroupcr.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=your-email@securitygroupcr.com

# Static Files
STATIC_ROOT=/app/staticfiles
MEDIA_ROOT=/app/media

# Logging
LOG_FILE=/app/logs/scg_presales.log
```

### 4. Create required directories:
```bash
mkdir -p staticfiles
mkdir -p logs
mkdir -p media
mkdir -p /var/certbot/conf
mkdir -p /var/certbot/www/.well-known/acme-challenge
```

## Step 3: Database Permissions Setup

### 1. Connect to your database with admin user and grant permissions:
```bash
# Connect to your Digital Ocean database with the admin user
psql -h your_db_host -U doadmin -d DB_SCG_PRESALES_PROD -p 25060
```

### 2. Run these SQL commands to grant permissions:
```sql
-- Grant database-level permissions
GRANT ALL PRIVILEGES ON DATABASE "DB_SCG_PRESALES_PROD" TO "SCG_PRESALES_USER";

-- Grant schema permissions
GRANT ALL PRIVILEGES ON SCHEMA public TO "SCG_PRESALES_USER";
GRANT CREATE ON SCHEMA public TO "SCG_PRESALES_USER";
GRANT USAGE ON SCHEMA public TO "SCG_PRESALES_USER";

-- Grant table permissions (for existing and future tables)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO "SCG_PRESALES_USER";
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO "SCG_PRESALES_USER";

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO "SCG_PRESALES_USER";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO "SCG_PRESALES_USER";

-- Make the user a database owner
ALTER DATABASE "DB_SCG_PRESALES_PROD" OWNER TO "SCG_PRESALES_USER";

-- Exit psql
\q
```

## Step 4: Deploy the Application (HTTP First)

### 1. Build and start the containers:
```bash
# Build the application
docker compose build

# Start the services
docker compose up -d
```

### 2. Check if containers are running:
```bash
docker compose ps
```

### 3. Check logs if needed:
```bash
# Backend logs
docker compose logs backend

# Nginx logs
docker compose logs nginx

# All logs
docker compose logs
```

## Step 5: Database Setup

### 1. Run database migrations:
```bash
# Create migrations for all custom apps
docker compose exec backend python manage.py makemigrations surveys
docker compose exec backend python manage.py makemigrations prospects
docker compose exec backend python manage.py makemigrations scoring
docker compose exec backend python manage.py makemigrations communications
docker compose exec backend python manage.py makemigrations reports
docker compose exec backend python manage.py makemigrations landing
docker compose exec backend python manage.py makemigrations admin_panel

# Apply all migrations
docker compose exec backend python manage.py migrate
```

### 2. Load survey data:
```bash
docker compose exec backend python manage.py load_survey_data
```

### 3. Create a superuser:
```bash
docker compose exec backend python manage.py createsuperuser
```

### 4. Collect static files:
```bash
docker compose exec backend python manage.py collectstatic --no-input
```

### 5. Test HTTP access:
```bash
# Test if the site is working on HTTP
curl -I http://securitygroupcr.com
# Should return HTTP/1.1 200 OK
```

## Step 6: SSL Certificate Setup

### 1. Test certbot challenge path:
```bash
# Create a test file to verify the challenge path works
echo "test123" > /var/certbot/www/.well-known/acme-challenge/testfile

# Test if it's accessible
curl http://securitygroupcr.com/.well-known/acme-challenge/testfile
# Should return "test123"

# Remove test file
rm /var/certbot/www/.well-known/acme-challenge/testfile
```

### 2. Get SSL certificates:
```bash
docker run --rm \
  -v /var/certbot/conf:/etc/letsencrypt \
  -v /var/certbot/www:/var/www/certbot \
  certbot/certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email itops@securitygroupcr.com \
  --agree-tos \
  --no-eff-email \
  -d securitygroupcr.com \
  -d www.securitygroupcr.com
```

### 3. Update nginx configuration for HTTPS:
```bash
# Create SSL-enabled nginx config
cat > nginx/conf.d/nginx.conf << 'EOF'
upstream web_app {
    server backend:8000;
}

server {
    listen 80;
    server_name securitygroupcr.com www.securitygroupcr.com;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl;
    http2 on;
    server_name securitygroupcr.com www.securitygroupcr.com;

    ssl_certificate /etc/letsencrypt/live/securitygroupcr.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/securitygroupcr.com/privkey.pem;

    ssl_session_cache shared:le_nginx_SSL:10m;
    ssl_session_timeout 1440m;
    ssl_session_tickets off;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;

    ssl_ciphers "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384";

    client_max_body_size 4G;
    keepalive_timeout 5;

    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    location /static/ {
        alias /app/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }

    location / {
        proxy_pass http://web_app;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header Host $host;
        proxy_redirect off;
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
    }
}
EOF
```

### 4. Restart nginx to apply SSL configuration:
```bash
docker compose restart nginx
```

### 5. Test HTTPS access:
```bash
# Test HTTPS access
curl -I https://securitygroupcr.com
# Should return HTTP/1.1 200 OK

# Test HTTP redirect to HTTPS
curl -I http://securitygroupcr.com
# Should return HTTP/1.1 301 Moved Permanently
```

## Step 7: SSL Certificate Renewal

### 1. Create a renewal script:
```bash
cat > /root/renew-ssl.sh << 'EOF'
#!/bin/bash
docker run --rm \
  -v /var/certbot/conf:/etc/letsencrypt \
  -v /var/certbot/www:/var/www/certbot \
  certbot/certbot renew --quiet
docker compose restart nginx
EOF

chmod +x /root/renew-ssl.sh
```

### 2. Add to crontab for automatic renewal:
```bash
crontab -e
# Add this line to run twice daily
0 12 * * * /root/renew-ssl.sh
```

## Step 8: Security and Firewall

### 1. Configure UFW firewall:
```bash
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
```

## Step 9: Application Updates

### 1. Update application:
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker compose down
docker compose build
docker compose up -d

# Run migrations if needed
docker compose exec backend python manage.py migrate
```

## Troubleshooting

### Common Issues:

1. **Volume mapping issues with nginx:**
   - If certbot challenge files aren't served, restart the entire stack:
   ```bash
   docker compose down
   docker compose up -d
   ```

2. **Database connection issues:**
   - Verify database credentials in env_config/production.env
   - Check Digital Ocean database firewall settings
   - Ensure droplet IP is whitelisted in database settings

3. **Migration issues:**
   - Create migrations for each app individually before running migrate
   - Check database permissions if migrations fail

4. **SSL certificate issues:**
   - Ensure the challenge path works before running certbot
   - Test with: `curl http://securitygroupcr.com/.well-known/acme-challenge/testfile`

### Useful Commands:

```bash
# Check container status
docker compose ps

# View logs
docker compose logs -f

# Restart specific service
docker compose restart backend

# Execute command in container
docker compose exec backend python manage.py shell

# Check nginx configuration
docker compose exec nginx nginx -t

# Check if files exist in container
docker compose exec nginx ls -la /var/www/certbot/.well-known/acme-challenge/
```

## Final Checklist

- [ ] Domain points to droplet IP
- [ ] Database permissions granted
- [ ] SSL certificates installed and working
- [ ] Database migrations applied
- [ ] Survey data loaded
- [ ] Static files collected and served
- [ ] Email functionality configured
- [ ] Firewall configured
- [ ] Certificate renewal automated
- [ ] Application accessible via HTTPS
- [ ] Admin user created
- [ ] HTTP redirects to HTTPS properly