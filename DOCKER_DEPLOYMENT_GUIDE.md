# 🐳 Profile Automation System - Docker Deployment Guide

## 🚀 Quick Start (15 minutes to deployment!)

### Prerequisites:
- EC2 instance with Amazon Linux 2023
- SSH access to your instance
- Your project files uploaded

---

## 📋 Step-by-Step Deployment:

### 1. Install Docker on EC2:
```bash
# Connect to your EC2 instance
ssh -i "your-key.pem" ec2-user@your-ec2-public-ip

# Install Docker
sudo dnf install -y docker

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to docker group
sudo usermod -aG docker ec2-user

# Logout and login again, or run:
newgrp docker
```

### 2. Install docker-compose:
```bash
# Install docker-compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Make it executable
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose --version
```

### 3. Upload Your Project:
```bash
# Create project directory
mkdir profile-automation
cd profile-automation

# Upload your project files (from your local machine)
scp -i "your-key.pem" -r "C:\path\to\your\project\*" ec2-user@your-ec2-ip:~/profile-automation/
```

### 4. Configure Environment:
```bash
# Copy environment example
cp environment.example .env

# Edit .env file with your actual values
nano .env
```

### 5. Deploy with One Command:
```bash
# Make deploy script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

---

## 🎯 What This Docker Setup Gives You:

### ✅ **Pre-built Environment:**
- Python 3.9+ with all dependencies
- Chrome + Firefox browsers
- Playwright automation tools
- Nginx web server
- Supervisor process manager

### ✅ **Professional Features:**
- Reverse proxy with nginx
- Rate limiting and security headers
- Health checks
- Automatic restarts
- Log management

### ✅ **Easy Management:**
- One command deployment
- Fast updates (30 seconds)
- Easy debugging
- Consistent environment

---

## 🔄 Future Updates (Super Fast!):

### Code Update Process:
```bash
# 1. Update your code
git pull  # or upload new files

# 2. Deploy update (30 seconds!)
./deploy.sh

# 3. Done! Zero downtime! 🚀
```

### Manual Commands:
```bash
# Stop app
docker-compose down

# Rebuild and start
docker-compose up --build -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

---

## 🌐 Access Your Application:

### URLs:
- **Main App:** `http://your-ec2-public-ip`
- **API Docs:** `http://your-ec2-public-ip/docs`
- **Health Check:** `http://your-ec2-public-ip/health`

### Default Admin User:
- **Username:** `admin`
- **Password:** `admin123`
- **⚠️ Change password after first login!**

---

## 🔧 Troubleshooting:

### Check Container Status:
```bash
docker-compose ps
docker-compose logs -f
```

### Restart Services:
```bash
docker-compose restart
docker-compose down && docker-compose up -d
```

### Check Resources:
```bash
docker stats
df -h
free -h
```

---

## 📊 Performance Features:

### **Nginx Optimization:**
- Gzip compression
- Rate limiting (10 req/s)
- Security headers
- Reverse proxy

### **FastAPI Optimization:**
- 4 worker processes
- Async handling
- Health checks
- Auto-restart

### **Browser Automation:**
- Pre-installed browsers
- Headless mode support
- Playwright optimization
- Resource management

---

## 🎉 Benefits of This Setup:

1. **Fast Deployment:** 15 minutes initial, 30 seconds updates
2. **Professional Quality:** Production-ready configuration
3. **Easy Maintenance:** One command management
4. **Scalable:** Easy to add more containers
5. **Reliable:** Auto-restart, health checks
6. **Secure:** Rate limiting, security headers

---

## 🚀 Ready to Deploy?

Your Profile Automation System will be:
- ✅ **Running in 15 minutes**
- ✅ **Professional quality**
- ✅ **Easy to maintain**
- ✅ **100% reliable**

**Run `./deploy.sh` and watch the magic happen!** 🎯
