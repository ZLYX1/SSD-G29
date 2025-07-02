# SSD-G29 Messaging System - Windows Docker Desktop Setup

This guide will help you set up and run the SSD-G29 messaging application using Windows Docker Desktop.

## 🎯 What This Includes

The messaging system provides:
- ✅ **End-to-End Encrypted Messaging Interface** (ready for encryption implementation)
- ✅ **Real-time Chat Interface** with conversation management
- ✅ **User Reporting System** for safety
- ✅ **Message History** and read receipts
- ✅ **Conversation Management** with user search
- ✅ **Modern UI** with Bootstrap 5 and Font Awesome
- ✅ **Database Integration** with PostgreSQL
- ✅ **Security Features** including CSRF protection

## 📋 Prerequisites

1. **Windows 10/11** with Docker Desktop support
2. **Docker Desktop for Windows** (latest version)
   - Download from: https://www.docker.com/products/docker-desktop/
3. **4GB+ RAM available** for Docker containers
4. **10GB+ free disk space**

## 🚀 Quick Start (Option 1: Automated Setup)

### Method A: Using Batch File
1. Double-click `start-windows.bat`
2. Wait for setup to complete
3. Access the application at http://localhost:5000

### Method B: Using PowerShell
1. Right-click `start-windows.ps1` → "Run with PowerShell"
2. If prompted about execution policies, choose "Yes"
3. Wait for setup to complete
4. Application will open automatically in your browser

## 🔧 Manual Setup (Option 2: Step by Step)

### Step 1: Ensure Docker Desktop is Running
```cmd
docker --version
docker-compose --version
```

### Step 2: Clone or Navigate to Project Directory
```cmd
cd "c:\Users\Ryan\School Stuff\Year 2\Trimester 3\Secure Software Development\Project\SSD-G29"
```

### Step 3: Environment Configuration
The `.env` file is already configured for development. Key settings:
- Database: PostgreSQL with user `ssd_user`
- Flask running in development mode
- Debug mode enabled
- CSRF protection configured

### Step 4: Start the Application
```cmd
# Start all services
docker-compose -f docker-compose.dev.yml up --build -d

# Check if containers are running
docker-compose -f docker-compose.dev.yml ps

# View logs
docker-compose -f docker-compose.dev.yml logs -f
```

## 🌐 Accessing the Application

Once started, you can access:

| Service | URL | Purpose |
|---------|-----|---------|
| **Main App** | http://localhost:5000 | SSD-G29 Web Application |
| **Database** | localhost:5432 | PostgreSQL Direct Access |
| **pgAdmin** | http://localhost:8080 | Database Management UI |

### pgAdmin Login:
- **Email:** admin@ssd.local
- **Password:** admin123

## 💬 Using the Messaging System

### Default Test Users
The system comes with sample users for testing:
- **Seeker:** seeker@example.com / password123
- **Escort:** escort@example.com / password123
- **Admin:** admin@example.com / password123

### Features to Test:
1. **Login** with any test user
2. **Navigate to Messages** from the top menu
3. **Start New Conversation** using the "New" button
4. **Send Messages** with real-time interface
5. **Report Users** using the dropdown menu
6. **View Message History** and read receipts

## 🛠️ Development Commands

```cmd
# Stop all containers
docker-compose -f docker-compose.dev.yml down

# Restart with fresh build
docker-compose -f docker-compose.dev.yml up --build

# View specific service logs
docker-compose -f docker-compose.dev.yml logs web
docker-compose -f docker-compose.dev.yml logs db

# Access container shell
docker-compose -f docker-compose.dev.yml exec web bash

# Run database migrations
docker-compose -f docker-compose.dev.yml exec web flask db upgrade

# Reset database
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up --build -d
```

## 📁 Project Structure

```
SSD-G29/
├── 📄 docker-compose.dev.yml    # Development Docker configuration
├── 📄 Dockerfile               # Container build instructions
├── 📄 .env                     # Environment variables
├── 📄 start-windows.bat        # Windows setup script
├── 📄 start-windows.ps1        # PowerShell setup script
├── 📂 templates/
│   └── 📄 messaging.html       # Enhanced messaging interface
├── 📂 blueprint/
│   └── 📄 messaging.py         # Messaging routes and logic
├── 📂 controllers/
│   └── 📄 message_controller.py # Business logic for messaging
└── 📂 static/css/
    └── 📄 style.css            # Enhanced styling
```

## 🔍 Troubleshooting

### Docker Desktop Issues
```cmd
# Restart Docker Desktop if containers won't start
# Check Docker Desktop → Settings → Resources → Advanced
# Ensure at least 4GB RAM allocated

# Reset Docker if needed
docker system prune -a
```

### Port Conflicts
If ports 5000, 5432, or 8080 are already in use:
1. Stop the conflicting service
2. Or modify ports in `docker-compose.dev.yml`

### Database Connection Issues
```cmd
# Check if PostgreSQL container is healthy
docker-compose -f docker-compose.dev.yml logs db

# Reset database volume
docker-compose -f docker-compose.dev.yml down -v
docker volume rm ssd-g29_postgres_dev_data
docker-compose -f docker-compose.dev.yml up -d
```

### Application Won't Load
```cmd
# Check Flask container logs
docker-compose -f docker-compose.dev.yml logs web

# Restart web container
docker-compose -f docker-compose.dev.yml restart web
```

## 🔐 Security Notes

- **Development Mode:** CSRF protection is enabled but relaxed for localhost
- **Default Passwords:** Change default passwords before production
- **Encryption:** Message encryption framework is ready for implementation
- **Validation:** Input validation and XSS protection included

## 📞 Support

If you encounter issues:
1. Check Docker Desktop is running
2. Ensure no port conflicts exist
3. Review the logs using provided commands
4. Try the reset procedures above

## 🎯 Next Steps

The messaging system is now ready for:
1. **Encryption Implementation** - Add actual E2E encryption
2. **Real-time Updates** - Implement WebSocket for live messaging
3. **File Sharing** - Add file attachment capabilities
4. **Push Notifications** - Browser notification support
5. **Mobile Responsiveness** - Enhanced mobile experience

The foundation is solid and ready for advanced features!
