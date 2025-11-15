# Deployment Guide

This guide covers deploying the Project Manager API to production.

## Prerequisites

- Python 3.10+
- PostgreSQL database
- Domain name (optional)
- SSL certificate (for HTTPS)

## Deployment Options

### Option 1: Docker Deployment (Recommended)

#### 1. Install Docker and Docker Compose

```bash
# Linux
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 2. Configure Environment

Update `docker-compose.yml` with production values:
- Change `SECRET_KEY`
- Update database passwords
- Set `DEBUG=False`
- Configure `ALLOWED_HOSTS`
- Set `CORS_ALLOWED_ORIGINS`

#### 3. Deploy

```bash
# Build and start containers
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

#### 4. Check Status

```bash
docker-compose ps
docker-compose logs -f web
```

### Option 2: Traditional Server Deployment

#### 1. Prepare Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3.11 python3.11-venv python3-pip postgresql nginx -y
```

#### 2. Setup PostgreSQL

```bash
# Create database and user
sudo -u postgres psql

CREATE DATABASE project_manager_db;
CREATE USER project_manager_user WITH PASSWORD 'your_secure_password';
ALTER ROLE project_manager_user SET client_encoding TO 'utf8';
ALTER ROLE project_manager_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE project_manager_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE project_manager_db TO project_manager_user;
\q
```

#### 3. Setup Application

```bash
# Create app directory
sudo mkdir -p /var/www/project_manager
cd /var/www/project_manager

# Clone repository
git clone <your-repo-url> .

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn
```

#### 4. Configure Environment

Create `/var/www/project_manager/.env`:

```env
DEBUG=False
SECRET_KEY=your-very-secret-key-here-change-this
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com

DB_ENGINE=django.db.backends.postgresql
DB_NAME=project_manager_db
DB_USER=project_manager_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432

JWT_ACCESS_TOKEN_LIFETIME=30
JWT_REFRESH_TOKEN_LIFETIME=1440
```

#### 5. Run Migrations

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

#### 6. Setup Gunicorn Service

Create `/etc/systemd/system/project_manager.service`:

```ini
[Unit]
Description=Project Manager API
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/project_manager
Environment="PATH=/var/www/project_manager/venv/bin"
ExecStart=/var/www/project_manager/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/var/www/project_manager/project_manager.sock \
    project_manager.wsgi:application

[Install]
WantedBy=multi-user.target
```

Enable and start service:

```bash
sudo systemctl enable project_manager
sudo systemctl start project_manager
sudo systemctl status project_manager
```

#### 7. Configure Nginx

Create `/etc/nginx/sites-available/project_manager`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        return 301 https://$server_name$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;

    client_max_body_size 20M;

    location /static/ {
        alias /var/www/project_manager/staticfiles/;
    }

    location / {
        proxy_pass http://unix:/var/www/project_manager/project_manager.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/project_manager /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Option 3: Platform-as-a-Service (Heroku, Railway, etc.)

#### Heroku Deployment

1. **Install Heroku CLI**
```bash
curl https://cli-assets.heroku.com/install.sh | sh
```

2. **Login and Create App**
```bash
heroku login
heroku create your-app-name
```

3. **Add PostgreSQL**
```bash
heroku addons:create heroku-postgresql:mini
```

4. **Set Environment Variables**
```bash
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com
```

5. **Create Procfile**
```
web: gunicorn project_manager.wsgi --log-file -
release: python manage.py migrate
```

6. **Deploy**
```bash
git push heroku main
heroku run python manage.py createsuperuser
```

## Post-Deployment Checklist

- [ ] Database migrations completed
- [ ] Static files collected
- [ ] Superuser account created
- [ ] Environment variables configured
- [ ] SSL certificate installed
- [ ] HTTPS redirect working
- [ ] CORS configured correctly
- [ ] Health check endpoint accessible
- [ ] API documentation accessible
- [ ] Backup strategy implemented
- [ ] Monitoring setup
- [ ] Log rotation configured

## Monitoring

### Check Application Health

```bash
curl https://yourdomain.com/api/health/
```

### Monitor Logs

```bash
# Docker
docker-compose logs -f web

# Systemd
sudo journalctl -u project_manager -f

# Nginx
sudo tail -f /var/log/nginx/error.log
```

## Backup Strategy

### Database Backup

```bash
# PostgreSQL backup
pg_dump -U project_manager_user project_manager_db > backup.sql

# Automated daily backup
0 2 * * * pg_dump -U project_manager_user project_manager_db > /backups/db_$(date +\%Y\%m\%d).sql
```

### Application Backup

```bash
# Backup entire application
tar -czf project_manager_backup.tar.gz /var/www/project_manager
```

## Maintenance

### Update Application

```bash
cd /var/www/project_manager
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart project_manager
```

### Database Maintenance

```bash
# Vacuum database
sudo -u postgres vacuumdb -d project_manager_db -z

# Check database size
sudo -u postgres psql -c "SELECT pg_size_pretty(pg_database_size('project_manager_db'));"
```

## Scaling

### Horizontal Scaling

- Use load balancer (Nginx, HAProxy)
- Multiple Gunicorn instances
- Separate database server
- Redis for caching (optional)

### Vertical Scaling

- Increase Gunicorn workers
- Optimize database queries
- Add database indexes
- Enable query caching

## Security Best Practices

1. Keep SECRET_KEY secret and unique
2. Use strong database passwords
3. Enable firewall (UFW)
4. Regular security updates
5. Use SSL/TLS certificates
6. Implement rate limiting
7. Regular backups
8. Monitor logs for suspicious activity

## Troubleshooting

### Application won't start
```bash
# Check logs
sudo journalctl -u project_manager -n 50

# Test Gunicorn manually
cd /var/www/project_manager
source venv/bin/activate
gunicorn project_manager.wsgi:application
```

### Database connection errors
```bash
# Test database connection
sudo -u postgres psql -U project_manager_user -d project_manager_db

# Check PostgreSQL status
sudo systemctl status postgresql
```

### Static files not loading
```bash
# Recollect static files
python manage.py collectstatic --noinput

# Check Nginx configuration
sudo nginx -t

# Check file permissions
ls -la /var/www/project_manager/staticfiles/
```

## Support

For issues and support:
- Check logs first
- Review documentation
- Open GitHub issue
- Contact support team
