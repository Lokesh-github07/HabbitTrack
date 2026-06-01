# Deployment Guide

## Production Deployment Checklist

### 🔧 Server Configuration

1. **Update Flask Configuration**
```python
# In backend/config.py
class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True  # Only over HTTPS
    SESSION_COOKIE_HTTPONLY = True
```

2. **Update .env for Production**
```bash
FLASK_ENV=production
DEBUG=False
SECRET_KEY=generate-a-secure-random-key-here
DATABASE_URL=mysql+pymysql://prod_user:secure_password@db-server:3306/habittrack_prod
SESSION_COOKIE_SECURE=True
```

3. **Generate Secure Secret Key**
```python
import secrets
print(secrets.token_hex(32))
```

### 🚀 Deployment Options

#### Option 1: Traditional Server (VPS/Dedicated)

1. **Install Dependencies**
```bash
sudo apt update
sudo apt install python3 python3-pip mysql-server python3-venv
```

2. **Clone Application**
```bash
git clone your-repo habittrack
cd habittrack
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

3. **Setup Gunicorn**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app
```

4. **Setup Supervisor**
```bash
sudo apt install supervisor

sudo nano /etc/supervisor/conf.d/habittrack.conf
```

Add:
```ini
[program:habittrack]
directory=/home/user/habittrack
command=/home/user/habittrack/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 backend.app:app
autostart=true
autorestart=true
redirect_stderr=true
```

5. **Setup Nginx Reverse Proxy**
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        root /var/www/habittrack;
        try_files $uri /index.html;
    }

    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

6. **Enable HTTPS with Let's Encrypt**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

#### Option 2: Heroku

1. **Create Procfile**
```
web: gunicorn backend.app:app
```

2. **Deploy**
```bash
heroku login
heroku create your-app-name
git push heroku main
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-secret-key
heroku run python backend/app.py db upgrade
```

#### Option 3: Docker

1. **Create Dockerfile**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "backend.app:app"]
```

2. **Build and Run**
```bash
docker build -t habittrack .
docker run -p 5000:5000 -e DATABASE_URL=your_db_url habittrack
```

#### Option 4: AWS

1. **RDS for MySQL**
- Create RDS MySQL instance
- Update DATABASE_URL with RDS endpoint

2. **Elastic Beanstalk**
```bash
eb init -p python-3.9 habittrack
eb create habittrack-env
eb deploy
```

3. **CloudFront for Static Files**
- Upload frontend files to S3
- Setup CloudFront distribution

### 🗄️ Database Production Setup

1. **MySQL Configuration**
```bash
# Backup local database
mysqldump -u root habittrack > habittrack.sql

# Restore to production server
mysql -h prod-db-host -u prod_user -p habittrack < habittrack.sql
```

2. **Database Optimization**
```sql
-- Create indexes
CREATE INDEX idx_user_habits ON habits(user_id);
CREATE INDEX idx_habit_completions ON habit_completions(habit_id, date);

-- Enable query caching
SET GLOBAL query_cache_size = 268435456;
SET GLOBAL query_cache_type = ON;
```

3. **Backup Strategy**
```bash
# Daily backup
0 2 * * * mysqldump -u root -p habittrack | gzip > /backup/habittrack-$(date +\%Y\%m\%d).sql.gz

# Upload to cloud storage
gs://habittrack-backups/$(date +%Y%m%d)/habittrack.sql.gz
```

### 📊 Monitoring & Logging

1. **Application Logging**
```python
import logging
logging.basicConfig(filename='/var/log/habittrack.log', level=logging.INFO)
```

2. **Error Tracking (Sentry)**
```bash
pip install sentry-sdk

import sentry_sdk
sentry_sdk.init("your-sentry-dsn")
```

3. **Performance Monitoring**
- Use New Relic or Datadog
- Monitor CPU, Memory, Database queries

### 🔒 Security Checklist

- [ ] HTTPS enabled
- [ ] Secure secret key generated
- [ ] Database credentials in environment variables
- [ ] SQL injection protection (using ORM)
- [ ] CORS configured for specific domain
- [ ] CSRF protection enabled
- [ ] Password hashing implemented
- [ ] Rate limiting configured
- [ ] API authentication required
- [ ] Firewall rules configured
- [ ] Database backups automated
- [ ] Log monitoring enabled
- [ ] Error tracking setup
- [ ] Security headers configured

### 📋 Post-Deployment

1. **Test All Features**
- User registration
- Login/Logout
- Habit CRUD operations
- Analytics charts
- Responsive design on mobile

2. **Performance Testing**
```bash
# Load testing with Apache Bench
ab -n 1000 -c 10 https://yourdomain.com/api/auth/verify-token
```

3. **Security Testing**
- Run OWASP ZAP scan
- Check for SQL injection vulnerabilities
- Verify HTTPS/TLS setup

4. **Monitor First Week**
- Watch error logs
- Monitor database performance
- Track user registration rate

### 🔄 Continuous Deployment

1. **GitHub Actions**
Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to server
        env:
          DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
        run: |
          ssh -i $DEPLOY_KEY user@server 'cd /home/user/habittrack && git pull && pip install -r requirements.txt && systemctl restart habittrack'
```

2. **Docker Registry**
```bash
# Build and push to Docker Hub
docker build -t yourusername/habittrack:latest .
docker push yourusername/habittrack:latest
```

### 📈 Scaling Strategies

1. **Load Balancing**
- Use Nginx/HAProxy
- Multiple application servers
- Session persistence

2. **Caching**
- Redis for session caching
- CloudFront for static files
- Database query caching

3. **Database Optimization**
- Read replicas
- Query optimization
- Connection pooling

### 💾 Disaster Recovery

1. **Backup Plan**
- Daily automated backups
- Weekly off-site backups
- Monthly archives

2. **Restore Procedure**
```bash
# Restore from backup
mysql habittrack < backup.sql
```

3. **Monitoring Uptime**
- UptimeRobot monitoring
- Alert on failures
- 99.9% uptime SLA

### 📞 Support & Maintenance

- Monitor error logs daily
- Review analytics weekly
- Update dependencies monthly
- Security patches immediately
- Database optimization quarterly

## Cost Estimation

### Hosting Options
| Service | Cost | Notes |
|---------|------|-------|
| Heroku | $7-50/month | Easiest setup |
| AWS EC2 | $5-100/month | More control |
| DigitalOcean | $4-24/month | Best value |
| Google Cloud | $10-200/month | Enterprise |

### Total Monthly Cost
- Server: $20
- Database: $15
- CDN: $10
- Email: $20
- Monitoring: $10
- **Total: ~$75/month**

---

For questions or issues with deployment, refer to framework documentation:
- Flask: https://flask.palletsprojects.com/
- MySQL: https://dev.mysql.com/
- Gunicorn: https://gunicorn.org/
