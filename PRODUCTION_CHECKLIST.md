# Production Deployment Checklist

## Pre-Deployment Verification

### ✅ Code Quality
- [x] All tests passing (7/7)
- [x] No syntax errors
- [x] No critical security warnings
- [x] Code follows best practices
- [x] Proper error handling implemented
- [x] Logging configured

### ✅ Database
- [x] All migrations created
- [x] All migrations applied
- [x] Models have proper ordering
- [x] Models have __str__ methods
- [x] Foreign keys properly indexed

### ✅ Security
- [x] SECRET_KEY from environment
- [x] DEBUG=False in production
- [x] ALLOWED_HOSTS configured
- [x] CORS properly restricted
- [x] CSRF protection enabled
- [x] JWT authentication working
- [x] Permissions enforced
- [x] SQL injection protected (ORM)
- [x] XSS protection enabled

### ✅ API
- [x] All endpoints tested
- [x] Pagination implemented
- [x] Filtering working
- [x] Search functional
- [x] Ordering available
- [x] Error responses standardized
- [x] API documentation available

### ✅ Files & Configuration
- [x] .gitignore configured
- [x] .env.example provided
- [x] requirements.txt complete
- [x] README.md comprehensive
- [x] DEPLOYMENT.md included
- [x] Docker files ready

---

## Deployment Steps

### Step 1: Environment Setup
```bash
# Create production .env file
cp .env.example .env

# Update production values:
DEBUG=False
SECRET_KEY=<generate-secure-key>
ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=<production-database>
```

### Step 2: Database Setup
```bash
# For PostgreSQL
CREATE DATABASE project_manager_prod;
CREATE USER pm_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE project_manager_prod TO pm_user;

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Step 3: Static Files
```bash
# Collect static files
python manage.py collectstatic --noinput
```

### Step 4: Test Production Settings
```bash
# Check deployment config
python manage.py check --deploy

# Should show 0 critical issues
```

### Step 5: Start Production Server
```bash
# With Gunicorn
gunicorn project_manager.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 60 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log
```

---

## Post-Deployment Verification

### Health Checks
- [ ] Health endpoint responds: `/api/health/`
- [ ] API docs accessible: `/api/docs/`
- [ ] Admin panel accessible: `/admin/`
- [ ] Registration working
- [ ] Login working
- [ ] Token refresh working
- [ ] All CRUD operations functional

### Performance Checks
- [ ] Response times < 200ms
- [ ] Database queries optimized
- [ ] Pagination working correctly
- [ ] No memory leaks
- [ ] No N+1 query problems

### Security Checks
- [ ] HTTPS enforced
- [ ] HSTS headers present
- [ ] CORS restricted
- [ ] CSRF tokens working
- [ ] JWT tokens expiring correctly
- [ ] Rate limiting active (if implemented)

### Monitoring
- [ ] Error logging working
- [ ] Access logs captured
- [ ] Health checks automated
- [ ] Alerts configured
- [ ] Backup schedule set

---

## Environment Variables Required

### Required
```
SECRET_KEY=<50+ char random string>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_ENGINE=django.db.backends.postgresql
DB_NAME=project_manager_prod
DB_USER=pm_user
DB_PASSWORD=<secure-password>
DB_HOST=localhost
DB_PORT=5432
```

### Optional
```
CORS_ALLOWED_ORIGINS=https://yourdomain.com
JWT_ACCESS_TOKEN_LIFETIME=30
JWT_REFRESH_TOKEN_LIFETIME=1440
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=<your-email>
EMAIL_HOST_PASSWORD=<app-password>
```

---

## Server Requirements

### Minimum Specifications
- **CPU**: 1 vCPU
- **RAM**: 512 MB
- **Storage**: 10 GB
- **Bandwidth**: 1 TB/month

### Recommended Specifications
- **CPU**: 2 vCPUs
- **RAM**: 2 GB
- **Storage**: 20 GB SSD
- **Bandwidth**: Unlimited

### Software Requirements
- Python 3.10+
- PostgreSQL 12+
- Nginx (recommended)
- Gunicorn
- Supervisor (process manager)

---

## Nginx Configuration

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    client_max_body_size 20M;

    location /static/ {
        alias /var/www/project_manager/staticfiles/;
        expires 30d;
    }

    location /media/ {
        alias /var/www/project_manager/media/;
        expires 30d;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Backup Strategy

### Database Backups
```bash
# Daily backup
0 2 * * * pg_dump -U pm_user project_manager_prod > /backups/db_$(date +\%Y\%m\%d).sql

# Weekly cleanup (keep 30 days)
0 3 * * 0 find /backups -name "db_*.sql" -mtime +30 -delete
```

### Code Backups
```bash
# Use Git tags for releases
git tag -a v1.0.0 -m "Production release v1.0.0"
git push origin v1.0.0
```

---

## Monitoring & Alerts

### Recommended Tools
- **Uptime**: UptimeRobot, Pingdom
- **Errors**: Sentry
- **Performance**: New Relic, DataDog
- **Logs**: Papertrail, Loggly

### Health Check Endpoint
Monitor: `https://yourdomain.com/api/health/`

Expected Response:
```json
{
  "status": "healthy",
  "database": "healthy",
  "api": "operational"
}
```

---

## SSL/TLS Certificate

### Using Let's Encrypt (Free)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### Auto-renewal
```bash
# Test renewal
sudo certbot renew --dry-run

# Add to crontab
0 0 1 * * certbot renew --quiet
```

---

## Troubleshooting

### 500 Internal Server Error
- Check error logs: `tail -f logs/error.log`
- Check DEBUG setting is False
- Verify SECRET_KEY is set
- Check database connection

### Static Files Not Loading
- Run `collectstatic` again
- Check Nginx configuration
- Verify file permissions
- Check STATIC_ROOT setting

### Database Connection Error
- Verify PostgreSQL is running
- Check database credentials
- Verify host/port settings
- Check firewall rules

### Permission Denied Errors
- Check file/folder ownership
- Verify user permissions
- Check SELinux settings (if enabled)

---

## Performance Optimization

### Database
- [ ] Add indexes to frequently queried fields
- [ ] Enable connection pooling
- [ ] Configure query caching
- [ ] Regular VACUUM ANALYZE

### Application
- [ ] Enable Django caching
- [ ] Use select_related/prefetch_related
- [ ] Compress responses (gzip)
- [ ] Enable HTTP/2

### Server
- [ ] Configure worker processes (CPU cores + 1)
- [ ] Set appropriate timeouts
- [ ] Enable keepalive
- [ ] Configure max requests per worker

---

## Maintenance Schedule

### Daily
- Monitor error logs
- Check disk space
- Review access logs
- Verify backups completed

### Weekly
- Review performance metrics
- Check for security updates
- Test backup restoration
- Review user feedback

### Monthly
- Update dependencies
- Security audit
- Database maintenance
- Review and optimize queries

### Quarterly
- Major version updates
- Comprehensive security review
- Disaster recovery test
- Capacity planning review

---

## Rollback Plan

### If Deployment Fails
1. Keep previous version running
2. Fix issues in development
3. Re-test thoroughly
4. Deploy again

### Quick Rollback
```bash
# If using Git deployment
git reset --hard <previous-commit>
git push -f

# Restart services
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

---

## Documentation Links

- **Main README**: README.md
- **Deployment Guide**: DEPLOYMENT.md
- **API Documentation**: /api/docs/
- **Frontend Guide**: FRONTEND_GUIDE.md
- **Contributing**: CONTRIBUTING.md

---

## Success Criteria

### Your deployment is successful when:
- ✅ All health checks pass
- ✅ All endpoints respond correctly
- ✅ No errors in logs (first 24 hours)
- ✅ Response times within acceptable range
- ✅ Users can register and login
- ✅ All features work as expected
- ✅ Backups are running
- ✅ Monitoring is active
- ✅ SSL certificate valid

---

## Post-Launch Tasks

- [ ] Announce launch
- [ ] Monitor closely for 72 hours
- [ ] Gather user feedback
- [ ] Address any issues quickly
- [ ] Document any problems/solutions
- [ ] Update documentation as needed
- [ ] Plan next iteration

---

**Need Help?**
- Review logs: `tail -f logs/error.log`
- Check deployment guide: `DEPLOYMENT.md`
- Test locally first
- Use staging environment
- Have rollback plan ready

**Remember:** Test everything in staging before production!
