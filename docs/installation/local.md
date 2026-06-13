# 💻 Local Installation

Install Xiaozhi ESP32 Server directly on your system for maximum control and customization. This method is ideal for developers and users who prefer local control over their environment.

## 🎯 Why Local Installation?

### **✅ Advantages**
- **Full system control** - access to all system resources
- **Easy debugging** - direct access to logs and processes
- **Custom modifications** - modify code and configuration freely
- **Development friendly** - ideal for contributing to the project
- **No Docker overhead** - direct system performance

### **⚠️ Considerations**
- **System dependencies** - requires Python, Node.js, and other tools
- **Platform differences** - setup varies by operating system
- **Manual updates** - requires manual dependency management
- **Environment conflicts** - potential package conflicts

## 📋 Prerequisites

### **System Requirements**
- **Python 3.10+** with pip
- **Node.js 16+** with npm/pnpm
- **Git** for version control
- **MySQL 8.0+** or **PostgreSQL 13+**
- **Redis 6+** for caching
- **FFmpeg** for audio processing
- **Libopus** for audio codecs

### **Operating System Specific**

#### **Windows**
```powershell
# Install Python
winget install Python.Python.3.10

# Install Node.js
winget install OpenJS.NodeJS

# Install Git
winget install Git.Git

# Install MySQL
winget install Oracle.MySQL
```

#### **macOS**
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python@3.10 node git mysql redis ffmpeg opus
```

#### **Linux (Ubuntu/Debian)**
```bash
# Update package list
sudo apt update

# Install dependencies
sudo apt install python3.10 python3.10-venv python3-pip nodejs npm git mysql-server redis-server ffmpeg libopus-dev
```

## 🚀 Installation Steps

### **Step 1: Clone Repository**

```bash
# Clone the repository
git clone https://github.com/lapy/xiaozhi-esp32-server.git
cd xiaozhi-esp32-server
```

### **Step 2: Set Up Python Environment**

```bash
# Create virtual environment
python3.10 -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### **Step 3: Install Python Dependencies**

```bash
# Navigate to server directory
cd main/xiaozhi-server

# Install requirements
pip install -r requirements.txt

# Install additional dependencies
pip install mysql-connector-python redis
```

### **Step 4: Set Up Database**

#### **MySQL Setup**

```bash
# Start MySQL service
# Windows: Start MySQL service
# macOS: brew services start mysql
# Linux: sudo systemctl start mysql

# Create database
mysql -u root -p
```

```sql
CREATE DATABASE xiaozhi CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'xiaozhi'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON xiaozhi.* TO 'xiaozhi'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### **PostgreSQL Setup**

```bash
# Start PostgreSQL service
# Windows: Start PostgreSQL service
# macOS: brew services start postgresql
# Linux: sudo systemctl start postgresql

# Create database
sudo -u postgres psql
```

```sql
CREATE DATABASE xiaozhi;
CREATE USER xiaozhi WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE xiaozhi TO xiaozhi;
\q
```

### **Step 5: Set Up Redis**

```bash
# Start Redis service
# Windows: Start Redis service
# macOS: brew services start redis
# Linux: sudo systemctl start redis

# Test Redis connection
redis-cli ping
# Should return: PONG
```

### **Step 6: Install Node.js Dependencies**

```bash
# Navigate to web interface
cd main/manager-web

# Install dependencies
npm install

# Build for production
npm run build
```

```bash
# Navigate to mobile interface
cd main/manager-mobile

# Install dependencies
pnpm install

# Build for production
pnpm run build
```

### **Step 7: Configure Environment**

Create environment configuration files:

```bash
# Create environment file
cat > .env << EOF
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_NAME=xiaozhi
DB_USER=xiaozhi
DB_PASSWORD=your_password

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
WEB_PORT=8001
API_PORT=8002
OTA_PORT=8003

# Security
JWT_SECRET=your_jwt_secret_key
ENCRYPTION_KEY=your_encryption_key

# AI Providers
OPENAI_API_KEY=your_openai_api_key
GROQ_API_KEY=your_groq_api_key
EOF
```

## ⚙️ Configuration

### **Server Configuration**

```bash
# Create data directory
mkdir -p data

# Create configuration file
cat > data/.config.yaml << EOF
# Server Configuration
server:
  host: 0.0.0.0
  port: 8000
  websocket: ws://localhost:8000/xiaozhi/v1/

# AI Provider Configuration
selected_module:
  ASR: WhisperASR
  LLM: OpenAILLM
  TTS: EdgeTTS

ASR:
  WhisperASR:
    type: whisper
    model_name: base
    device: auto
    language: null

LLM:
  OpenAILLM:
    type: openai
    api_key: your_openai_api_key
    model_name: gpt-4o-mini

TTS:
  EdgeTTS:
    type: edge_tts
    voice: en-US-AriaNeural
EOF
```

### **Database Migration**

```bash
# Run database migrations
cd main/manager-api
mvn flyway:migrate

# Or using Python
cd main/xiaozhi-server
python -m alembic upgrade head
```

## 🚀 Starting Services

### **Development Mode**

```bash
# Start all services in development mode
# Terminal 1: Start main server
cd main/xiaozhi-server
python app.py

# Terminal 2: Start web interface
cd main/manager-web
npm run serve

# Terminal 3: Start API server
cd main/manager-api
mvn spring-boot:run
```

### **Production Mode**

```bash
# Start with process manager (PM2)
npm install -g pm2

# Create PM2 ecosystem file
cat > ecosystem.config.js << EOF
module.exports = {
  apps: [
    {
      name: 'xiaozhi-server',
      script: 'main/xiaozhi-server/app.py',
      interpreter: 'python',
      cwd: '.',
      env: {
        NODE_ENV: 'production'
      }
    },
    {
      name: 'manager-web',
      script: 'main/manager-web/server.js',
      cwd: 'main/manager-web',
      env: {
        NODE_ENV: 'production'
      }
    },
    {
      name: 'manager-api',
      script: 'main/manager-api/target/xiaozhi-manager-api.jar',
      cwd: 'main/manager-api',
      env: {
        SPRING_PROFILES_ACTIVE: 'production'
      }
    }
  ]
};
EOF

# Start all services
pm2 start ecosystem.config.js

# Save PM2 configuration
pm2 save
pm2 startup
```

### **System Service (Linux)**

```bash
# Create systemd service files
sudo tee /etc/systemd/system/xiaozhi-server.service > /dev/null << EOF
[Unit]
Description=Xiaozhi ESP32 Server
After=network.target mysql.service redis.service

[Service]
Type=simple
User=xiaozhi
WorkingDirectory=/opt/xiaozhi-esp32-server
ExecStart=/opt/xiaozhi-esp32-server/venv/bin/python main/xiaozhi-server/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl enable xiaozhi-server
sudo systemctl start xiaozhi-server
```

## 🧪 Testing Installation

### **Health Checks**

```bash
# Test server health
curl http://localhost:8000/health

# Test web interface
curl http://localhost:8001

# Test API
curl http://localhost:8002/api/health

# Test OTA interface
curl http://localhost:8003/xiaozhi/ota/
```

### **Database Connection**

```bash
# Test database connection
python -c "
import mysql.connector
conn = mysql.connector.connect(
    host='localhost',
    user='xiaozhi',
    password='your_password',
    database='xiaozhi'
)
print('Database connection successful!')
conn.close()
"
```

### **Redis Connection**

```bash
# Test Redis connection
python -c "
import redis
r = redis.Redis(host='localhost', port=6379)
print('Redis connection successful!')
print('Ping:', r.ping())
"
```

## 🛠️ Troubleshooting

### **Common Issues**

#### **Python Dependencies**
```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Check for conflicts
pip check

# Update pip and setuptools
pip install --upgrade pip setuptools wheel
```

#### **Database Connection Issues**
```bash
# Check MySQL status
sudo systemctl status mysql

# Check MySQL logs
sudo tail -f /var/log/mysql/error.log

# Test connection
mysql -u xiaozhi -p -h localhost xiaozhi
```

#### **Redis Connection Issues**
```bash
# Check Redis status
sudo systemctl status redis

# Check Redis logs
sudo tail -f /var/log/redis/redis-server.log

# Test connection
redis-cli ping
```

#### **Port Conflicts**
```bash
# Check port usage
netstat -tulpn | grep :8000
netstat -tulpn | grep :8001
netstat -tulpn | grep :8002
netstat -tulpn | grep :8003

# Kill processes using ports
sudo fuser -k 8000/tcp
sudo fuser -k 8001/tcp
sudo fuser -k 8002/tcp
sudo fuser -k 8003/tcp
```

### **Performance Optimization**

#### **Python Optimization**
```bash
# Use optimized Python
export PYTHONOPTIMIZE=1

# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/main/xiaozhi-server"

# Use faster JSON library
pip install orjson
```

#### **Database Optimization**
```sql
-- Optimize MySQL settings
SET GLOBAL innodb_buffer_pool_size = 1G;
SET GLOBAL max_connections = 200;
SET GLOBAL query_cache_size = 64M;
```

#### **Redis Optimization**
```bash
# Configure Redis for performance
echo "maxmemory 512mb" >> /etc/redis/redis.conf
echo "maxmemory-policy allkeys-lru" >> /etc/redis/redis.conf
sudo systemctl restart redis
```

## 🔧 Development Setup

### **IDE Configuration**

#### **Visual Studio Code**
```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.terminal.activateEnvironment": true,
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true
  }
}
```

#### **PyCharm**
- Set Python interpreter to virtual environment
- Configure run configurations for each service
- Set up debugging breakpoints

### **Code Quality Tools**

```bash
# Install development tools
pip install black flake8 mypy pytest

# Format code
black main/xiaozhi-server/

# Lint code
flake8 main/xiaozhi-server/

# Type checking
mypy main/xiaozhi-server/

# Run tests
pytest main/xiaozhi-server/test/
```

## 📊 Monitoring

### **Log Management**

```bash
# View logs
tail -f logs/xiaozhi-server.log
tail -f logs/manager-api.log
tail -f logs/manager-web.log

# Rotate logs
sudo logrotate -f /etc/logrotate.d/xiaozhi
```

### **Performance Monitoring**

```bash
# Monitor system resources
htop
iotop
nethogs

# Monitor Python processes
ps aux | grep python
top -p $(pgrep python)
```

## 🎯 Next Steps

### **After Installation**

1. **[Configure AI Providers](../configuration/providers.md)** - Set up your AI services
2. **[Basic Setup](../configuration/basic-setup.md)** - Configure server settings
3. **[Connect ESP32 Device](../getting-started/first-device.md)** - Add your first device
4. **[Test Voice Interaction](../features/voice-interaction.md)** - Verify everything works

### **Advanced Topics**

- **[Cloud Deployment](cloud.md)** - Deploy to cloud platforms
- **[Docker Installation](docker.md)** - Alternative installation method
- **[Troubleshooting](troubleshooting.md)** - Common issues and solutions

## 🆘 Need Help?

- **Installation Issues?** Check [Troubleshooting](troubleshooting.md)
- **Configuration Problems?** See [Configuration Guide](../configuration/basic-setup.md)
- **Development Questions?** Browse [Contributing Guide](../support/contributing.md)

---

## 🎯 Quick Reference

### **Essential Commands**
```bash
# Start development server
python main/xiaozhi-server/app.py

# Start web interface
cd main/manager-web && npm run serve

# Start API server
cd main/manager-api && mvn spring-boot:run

# Check service status
pm2 status
```

### **Key URLs**
- **Web Interface**: http://localhost:8001
- **API Documentation**: http://localhost:8002/api/docs
- **OTA Interface**: http://localhost:8003/xiaozhi/ota/

### **Important Files**
- **Environment**: `.env`
- **Config**: `data/.config.yaml`
- **Logs**: `logs/` directory
- **Database**: MySQL/PostgreSQL

---

**Your local Xiaozhi installation is ready! 🎉**

👉 **[Next: Configure AI Providers →](../configuration/providers.md)**
