# Digital Ocean Deployment Guide

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

# Add user to docker group (optional, for non-root user)
usermod -aG docker $USER
```

### 4. Install Git:
```bash
apt install git -y
```

### 5. Create directories for SSL certificates:
```bash
mkdir -p /var/certbot/conf
mkdir -p /var/certbot/www
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
DB_NAME=your_db_name
DB_USER=your_db_user
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
```

## Step 3: SSL Certificate Setup

### 1. First, get SSL certificates using certbot:
```bash
# Run this command to get initial certificates
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

**Note:** You might need to temporarily serve the domain on port 80 first. If the above fails, follow these steps:

1. Create a temporary nginx configuration:
```bash
# Create temporary nginx config
mkdir -p /tmp/nginx
cat > /tmp/nginx/default.conf << 'EOF'
server {
    listen 80;
    server_name securitygroupcr.com;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 200 'OK';
        add_header Content-Type text/plain;
    }
}
EOF

# Run temporary nginx
docker run --rm -d \
  --name temp-nginx \
  -p 80:80 \
  -v /tmp/nginx:/etc/nginx/conf.d \
  -v /var/certbot/www:/var/www/certbot \
  nginx:alpine
```

2. Then run certbot:
```bash
docker run --rm \
  -v /var/certbot/conf:/etc/letsencrypt \
  -v /var/certbot/www:/var/www/certbot \
  certbot/certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email your-email@securitygroupcr.com \
  --agree-tos \
  --no-eff-email \
  -d securitygroupcr.com

# Stop temporary nginx
docker stop temp-nginx
```

## Step 4: Deploy the Application

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
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate
```

### 2. Create a superuser:
```bash
docker compose exec backend python manage.py createsuperuser
```

### 3. Collect static files:
```bash
docker compose exec backend python manage.py collectstatic --no-input
```

## Step 6: SSL Certificate Renewal

### 1. Create a renewal script:
```bash
cat > /root/renew-ssl.sh << 'EOF'
#!/bin/bash
docker compose exec certbot certbot renew --quiet
docker compose exec nginx nginx -s reload
EOF

chmod +x /root/renew-ssl.sh
```

### 2. Add to crontab for automatic renewal:
```bash
crontab -e
# Add this line to run twice daily
0 12 * * * /root/renew-ssl.sh
```

## Step 7: Monitoring and Maintenance

### 1. Check application health:
```bash
# Check if site is accessible
curl -I https://securitygroupcr.com

# Check container status
docker compose ps

# Check logs
docker compose logs -f backend
```

### 2. Update application:
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

## Step 8: Security and Firewall

### 1. Configure UFW firewall:
```bash
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
```

### 2. Regular security updates:
```bash
# Add to crontab
crontab -e
# Add this line for weekly updates
0 2 * * 0 apt update && apt upgrade -y
```

## Troubleshooting

### Common Issues:

1. **Certificate issues:**
   - Check that your domain points to the correct IP
   - Ensure port 80 is accessible during certificate creation
   - Check certbot logs: `docker compose logs certbot`

2. **Database connection issues:**
   - Verify database credentials in .env/production.env
   - Check Digital Ocean database firewall settings
   - Ensure droplet IP is whitelisted in database settings

3. **Static files not loading:**
   - Run collectstatic: `docker compose exec backend python manage.py collectstatic --no-input`
   - Check nginx logs: `docker compose logs nginx`

4. **Application not starting:**
   - Check backend logs: `docker compose logs backend`
   - Verify environment variables in env_config/production.env
   - Check database connectivity

### Useful Commands:

```bash
# Restart all services
docker compose restart

# Restart specific service
docker compose restart backend

# View real-time logs
docker compose logs -f

# Execute command in container
docker compose exec backend python manage.py shell

# Check disk space
df -h

# Check memory usage
free -h

# Check running processes
htop
```

## Backup Strategy

### 1. Database backups:
```bash
# Create backup script
cat > /root/backup-db.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/root/backups"
mkdir -p $BACKUP_DIR

# Database backup (adjust connection details)
pg_dump -h your_db_host -U your_db_user -d your_db_name > $BACKUP_DIR/db_backup_$DATE.sql

# Keep only last 7 backups
find $BACKUP_DIR -name "db_backup_*.sql" -mtime +7 -delete
EOF

chmod +x /root/backup-db.sh
```

### 2. Add to crontab:
```bash
crontab -e
# Add daily backup at 3 AM
0 3 * * * /root/backup-db.sh
```

## Performance Optimization

### 1. Increase worker count for production:
Edit `entrypoint.sh` and change:
```bash
gunicorn --env DJANGO_SETTINGS_MODULE=core.settings.production core.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

### 2. Add Redis for caching (optional):
Uncomment the cache configuration in `core/settings/production.py` and add Redis to docker-compose.yml if needed.

## Final Checklist

- [ ] Domain points to droplet IP
- [ ] SSL certificate installed and working
- [ ] Database connected and migrations applied
- [ ] Static files collected and served
- [ ] Email functionality tested
- [ ] Firewall configured
- [ ] Backup strategy in place
- [ ] Certificate renewal automated
- [ ] Application accessible via HTTPS
- [ ] Admin user created
- [ ] Logging working properly