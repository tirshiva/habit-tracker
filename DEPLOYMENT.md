# Deployment Guide

## Table of Contents
1. [Docker Container Management](#docker-container-management)
2. [AWS Deployment Guide](#aws-deployment-guide)
3. [Environment Configuration](#environment-configuration)
4. [Troubleshooting](#troubleshooting)

---

## Docker Container Management

### Prerequisites
- Docker and Docker Compose installed
- All environment variables configured (see [Environment Configuration](#environment-configuration))

### Starting the Application

```bash
# Navigate to project root
cd /path/to/habit-tracker

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f api
docker-compose logs -f frontend
docker-compose logs -f postgres
docker-compose logs -f redis
```

### Restarting Containers

#### Restart All Containers
```bash
# Stop all containers
docker-compose down

# Start all containers
docker-compose up -d

# Or restart in one command
docker-compose restart
```

#### Restart Specific Container
```bash
# Restart API only
docker-compose restart api

# Restart Frontend only
docker-compose restart frontend

# Restart Database only
docker-compose restart postgres

# Restart Redis only
docker-compose restart redis
```

#### Rebuild and Restart (After Code Changes)
```bash
# Stop containers
docker-compose down

# Rebuild images (with no cache for clean build)
docker-compose build --no-cache

# Start containers
docker-compose up -d

# Or rebuild and start in one command
docker-compose up -d --build
```

#### Restart with Database Migration
```bash
# Stop containers
docker-compose down

# Start containers (migrations run automatically via entrypoint.sh)
docker-compose up -d

# Check migration status
docker-compose exec api alembic current
docker-compose exec api alembic history
```

### Common Docker Commands

```bash
# View running containers
docker-compose ps

# View container status
docker-compose ps -a

# Stop all containers
docker-compose stop

# Stop and remove containers (keeps volumes)
docker-compose down

# Stop and remove containers with volumes (⚠️ deletes data)
docker-compose down -v

# Execute command in container
docker-compose exec api bash
docker-compose exec postgres psql -U postgres -d habit_tracker

# View container resource usage
docker stats

# Clean up unused resources
docker system prune -a
```

### Troubleshooting Docker Issues

```bash
# Check container logs for errors
docker-compose logs api | grep -i error
docker-compose logs frontend | grep -i error

# Check if containers are healthy
docker-compose ps

# Restart unhealthy container
docker-compose restart <service-name>

# Remove and recreate a specific container
docker-compose rm -f <service-name>
docker-compose up -d <service-name>

# Check network connectivity
docker network ls
docker network inspect habit_tracker_habit_tracker_network
```

---

## AWS Deployment Guide

### Architecture Overview

```
┌─────────────┐
│   Route 53  │ (Optional: Custom Domain)
└──────┬──────┘
       │
┌──────▼──────┐
│  CloudFront │ (CDN for Frontend)
└──────┬──────┘
       │
┌──────▼──────────────────┐
│  Application Load Balancer│
└──────┬───────────────────┘
       │
   ┌───┴───┐
   │       │
┌──▼──┐ ┌─▼───┐
│ EC2 │ │ EC2 │ (Auto Scaling Group)
└──┬──┘ └─┬───┘
   │      │
┌──▼──────▼──┐
│   RDS      │ (PostgreSQL)
└────────────┘
   │
┌──▼──────┐
│ ElastiCache│ (Redis)
└──────────┘
```

### Step 1: AWS Account Setup

1. **Create AWS Account** (if not already done)
2. **Install AWS CLI**
   ```bash
   # Linux
   curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
   unzip awscliv2.zip
   sudo ./aws/install

   # Configure AWS CLI
   aws configure
   ```

3. **Install Terraform** (Optional, for Infrastructure as Code)
   ```bash
   # Download from https://www.terraform.io/downloads
   ```

### Step 2: Create RDS PostgreSQL Database

```bash
# Using AWS CLI
aws rds create-db-instance \
  --db-instance-identifier habit-tracker-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username postgres \
  --master-user-password YOUR_SECURE_PASSWORD \
  --allocated-storage 20 \
  --vpc-security-group-ids sg-xxxxxxxxx \
  --db-subnet-group-name default \
  --backup-retention-period 7 \
  --publicly-accessible

# Note: Replace YOUR_SECURE_PASSWORD and sg-xxxxxxxxx with actual values
```

**Or use AWS Console:**
1. Go to RDS → Create Database
2. Choose PostgreSQL
3. Select Free Tier (db.t3.micro)
4. Configure:
   - DB Instance Identifier: `habit-tracker-db`
   - Master Username: `postgres`
   - Master Password: (strong password)
   - Public Access: Yes (or configure VPC properly)
5. Create database
6. Note the endpoint URL (e.g., `habit-tracker-db.xxxxx.us-east-1.rds.amazonaws.com`)

### Step 3: Create ElastiCache Redis

```bash
# Using AWS CLI
aws elasticache create-cache-cluster \
  --cache-cluster-id habit-tracker-redis \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1 \
  --security-group-ids sg-xxxxxxxxx

# Note: Replace sg-xxxxxxxxx with your security group
```

**Or use AWS Console:**
1. Go to ElastiCache → Create
2. Choose Redis
3. Configure:
   - Name: `habit-tracker-redis`
   - Node type: `cache.t3.micro`
   - Number of replicas: 0 (for development)
4. Create cluster
5. Note the endpoint URL

### Step 4: Create EC2 Instance

#### Option A: Single EC2 Instance (Development/Testing)

```bash
# Using AWS CLI
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.medium \
  --key-name your-key-pair \
  --security-group-ids sg-xxxxxxxxx \
  --subnet-id subnet-xxxxxxxxx \
  --user-data file://user-data.sh \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=HabitTracker}]'
```

**Or use AWS Console:**
1. Go to EC2 → Launch Instance
2. Choose Amazon Linux 2023 or Ubuntu 22.04
3. Instance type: `t3.medium` (minimum recommended)
4. Configure:
   - Key pair: Create or select existing
   - Network: Select VPC and subnet
   - Security Group: Create new with rules:
     - SSH (22): Your IP
     - HTTP (80): 0.0.0.0/0
     - HTTPS (443): 0.0.0.0/0
     - Custom TCP (8000): Security group only (for API)
5. Launch instance

#### Option B: Auto Scaling Group (Production)

1. Create Launch Template
2. Create Auto Scaling Group
3. Configure Load Balancer
4. Set up Health Checks

### Step 5: Setup EC2 Instance

SSH into your EC2 instance:

```bash
ssh -i your-key.pem ec2-user@your-ec2-ip
```

Install Docker and Docker Compose:

```bash
# Amazon Linux 2023
sudo yum update -y
sudo yum install docker -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login again for group changes
exit
```

### Step 6: Create Production Docker Compose File

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: habit_tracker_api
    restart: unless-stopped
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_HOST=${POSTGRES_HOST}
      - POSTGRES_PORT=${POSTGRES_PORT}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
      - ALGORITHM=${ALGORITHM}
      - ACCESS_TOKEN_EXPIRE_MINUTES=${ACCESS_TOKEN_EXPIRE_MINUTES}
      - SENTRY_DSN=${SENTRY_DSN}
      - RATE_LIMIT_PER_MINUTE=${RATE_LIMIT_PER_MINUTE}
      - ENVIRONMENT=production
      - LOG_LEVEL=${LOG_LEVEL}
    ports:
      - "8000:8000"
    networks:
      - habit_tracker_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        REACT_APP_API_URL: ${REACT_APP_API_URL}
    container_name: habit_tracker_frontend
    restart: unless-stopped
    ports:
      - "80:80"
    depends_on:
      - api
    networks:
      - habit_tracker_network

networks:
  habit_tracker_network:
    driver: bridge
```

### Step 7: Create Environment File

Create `.env.production` on EC2:

```bash
# Database (RDS)
DATABASE_URL=postgresql://postgres:PASSWORD@habit-tracker-db.xxxxx.us-east-1.rds.amazonaws.com:5432/habit_tracker
POSTGRES_USER=postgres
POSTGRES_PASSWORD=YOUR_SECURE_PASSWORD
POSTGRES_DB=habit_tracker
POSTGRES_HOST=habit-tracker-db.xxxxx.us-east-1.rds.amazonaws.com
POSTGRES_PORT=5432

# Redis (ElastiCache)
REDIS_URL=redis://habit-tracker-redis.xxxxx.cache.amazonaws.com:6379/0

# JWT
SECRET_KEY=your-super-secret-key-change-this-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
ENVIRONMENT=production
LOG_LEVEL=INFO
RATE_LIMIT_PER_MINUTE=60

# Frontend
REACT_APP_API_URL=/api/v1

# Sentry (Optional)
SENTRY_DSN=your-sentry-dsn-here
```

### Step 8: Deploy Application

On EC2 instance:

```bash
# Clone repository (or upload files)
git clone https://github.com/your-username/habit-tracker.git
cd habit-tracker

# Copy environment file
cp .env.production .env

# Build and start containers
docker-compose -f docker-compose.prod.yml up -d --build

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Step 9: Setup Nginx Reverse Proxy (Optional but Recommended)

Install Nginx:

```bash
sudo yum install nginx -y
sudo systemctl start nginx
sudo systemctl enable nginx
```

Create `/etc/nginx/conf.d/habit-tracker.conf`:

```nginx
upstream api_backend {
    server localhost:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # API
    location /api {
        proxy_pass http://api_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Restart Nginx:

```bash
sudo nginx -t
sudo systemctl restart nginx
```

### Step 10: Setup SSL with Let's Encrypt (Optional)

```bash
# Install Certbot
sudo yum install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### Step 11: Setup CloudFront (Optional - For CDN)

1. Go to CloudFront → Create Distribution
2. Origin Domain: Your EC2 public IP or domain
3. Viewer Protocol Policy: Redirect HTTP to HTTPS
4. Create Distribution
5. Update DNS to point to CloudFront URL

### Step 12: Setup Monitoring

#### CloudWatch Logs

```bash
# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
sudo rpm -U ./amazon-cloudwatch-agent.rpm

# Configure (follow prompts)
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard
```

#### CloudWatch Alarms

1. Go to CloudWatch → Alarms
2. Create alarms for:
   - CPU utilization > 80%
   - Memory utilization > 80%
   - Disk space < 20%
   - Application health check failures

### Step 13: Setup Auto-Scaling (Production)

1. Create Launch Template
2. Create Auto Scaling Group
3. Configure:
   - Min: 2 instances
   - Desired: 2 instances
   - Max: 5 instances
4. Set up scaling policies

### Step 14: Backup Strategy

#### Database Backups

RDS automatically creates backups, but you can also:

```bash
# Manual backup
pg_dump -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB > backup.sql

# Upload to S3
aws s3 cp backup.sql s3://your-backup-bucket/db-backups/
```

#### Application Backups

```bash
# Backup Docker volumes
docker run --rm -v habit_tracker_postgres_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/postgres-backup.tar.gz /data
```

---

## Environment Configuration

### Development (.env)

```bash
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=habit_tracker
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/habit_tracker

# Redis
REDIS_URL=redis://redis:6379/0

# JWT
SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
ENVIRONMENT=development
LOG_LEVEL=DEBUG
RATE_LIMIT_PER_MINUTE=60

# Frontend
REACT_APP_API_URL=http://localhost:8000/api/v1
```

### Production (.env.production)

See Step 7 above for production environment variables.

---

## Troubleshooting

### Database Connection Issues

```bash
# Test database connection
docker-compose exec api python -c "from app.database import engine; engine.connect()"

# Check database logs
docker-compose logs postgres

# Verify environment variables
docker-compose exec api env | grep POSTGRES
```

### API Not Starting

```bash
# Check API logs
docker-compose logs api

# Check if migrations ran
docker-compose exec api alembic current

# Run migrations manually
docker-compose exec api alembic upgrade head
```

### Frontend Not Loading

```bash
# Check frontend logs
docker-compose logs frontend

# Rebuild frontend
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

### Redis Connection Issues

```bash
# Test Redis connection
docker-compose exec redis redis-cli ping

# Check Redis logs
docker-compose logs redis
```

### AWS-Specific Issues

#### EC2 Instance Not Accessible

1. Check Security Groups (ports 80, 443, 22)
2. Check Network ACLs
3. Verify instance is running
4. Check route tables

#### RDS Connection Issues

1. Verify Security Group allows EC2 security group
2. Check RDS is publicly accessible (or in same VPC)
3. Verify credentials
4. Test connection: `psql -h $RDS_ENDPOINT -U postgres -d habit_tracker`

#### High Costs

1. Use Reserved Instances for RDS
2. Use Spot Instances for EC2 (non-production)
3. Enable auto-scaling down during low traffic
4. Use S3 for static assets instead of EC2 storage

---

## Security Checklist

- [ ] Change all default passwords
- [ ] Use strong SECRET_KEY (min 32 characters)
- [ ] Enable SSL/TLS (HTTPS)
- [ ] Configure Security Groups properly
- [ ] Use IAM roles instead of access keys
- [ ] Enable RDS encryption at rest
- [ ] Enable CloudTrail for audit logs
- [ ] Set up WAF (Web Application Firewall)
- [ ] Regular security updates
- [ ] Backup encryption enabled
- [ ] MFA enabled for AWS account
- [ ] Regular security scans

---

## Cost Estimation (Monthly)

### Development/Testing
- EC2 t3.medium: ~$30
- RDS db.t3.micro: ~$15
- ElastiCache cache.t3.micro: ~$15
- Data Transfer: ~$5
- **Total: ~$65/month**

### Production (Small Scale)
- EC2 t3.large (2 instances): ~$120
- RDS db.t3.small: ~$30
- ElastiCache cache.t3.small: ~$30
- Load Balancer: ~$20
- CloudFront: ~$10
- Data Transfer: ~$20
- **Total: ~$230/month**

### Production (Medium Scale)
- EC2 t3.xlarge (Auto Scaling): ~$300
- RDS db.t3.medium: ~$80
- ElastiCache cache.t3.medium: ~$80
- Load Balancer: ~$20
- CloudFront: ~$50
- Data Transfer: ~$100
- **Total: ~$630/month**

---

## Quick Reference Commands

```bash
# Local Development
docker-compose up -d
docker-compose logs -f
docker-compose restart api

# Production
docker-compose -f docker-compose.prod.yml up -d --build
docker-compose -f docker-compose.prod.yml logs -f
docker-compose -f docker-compose.prod.yml restart api

# Database
docker-compose exec api alembic upgrade head
docker-compose exec postgres psql -U postgres -d habit_tracker

# Monitoring
docker stats
docker-compose ps
aws cloudwatch get-metric-statistics ...
```

---

## Support

For issues or questions:
1. Check logs: `docker-compose logs -f`
2. Check AWS CloudWatch
3. Review this documentation
4. Check GitHub Issues

