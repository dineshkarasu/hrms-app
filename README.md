# HRMS Application

Human Resource Management System built with FastAPI (Python) backend and React frontend.

## 🚀 Quick Start

```bash
# Make scripts executable
chmod +x start.sh stop.sh

# Start the application
./start.sh
```

Access at: **http://localhost**

For detailed instructions, see [QUICKSTART.md](QUICKSTART.md)

## Structure

```
HRMS/
├── hrms-api/              # FastAPI backend
│   ├── Dockerfile         # API container image
│   ├── main.py           # FastAPI application
│   ├── database.py       # Database connection
│   ├── requirements.txt  # Python dependencies
│   ├── models/           # Database models & schemas
│   └── routers/          # API endpoints
│
├── hrms-web/             # React frontend
│   ├── Dockerfile        # Web container image
│   ├── nginx-internal.conf  # Nginx configuration
│   ├── package.json      # Node dependencies
│   └── src/              # React application
│
├── docker-compose.yml    # Service orchestration
├── nginx.conf            # Nginx reverse proxy config
├── start.sh              # Start script
├── stop.sh               # Stop script
└── .env.example          # Environment template
```

## Technology Stack

**Backend:**
- Python 3.11
- FastAPI
- PostgreSQL 15
- SQLAlchemy
- Pydantic

**Frontend:**
- React 18
- Axios
- React Router

## 🐳 Docker Deployment (Recommended)

Run the entire application with one command:

```bash
./start.sh
```

This starts:
- PostgreSQL database
- FastAPI backend
- React frontend
- Nginx reverse proxy

See [README-DOCKER.md](README-DOCKER.md) for detailed Docker documentation.

## 💻 Local Development (Without Docker)

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15

### Setup

1. **Database:**
```bash
docker run -d -p 5432:5432 \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=hrmsdb \
  postgres:15-alpine
```

2. **Backend:**
```bash
cd hrms-api
pip install -r requirements.txt
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/hrmsdb"
export ENVIRONMENT="dev"
uvicorn main:app --reload
```

3. **Frontend:**
```bash
cd hrms-web
npm install
npm start
```

## ⚙️ Configuration

Copy `.env.example` to `.env` and customize:
## ✨ Features

- **Employee Management** - Create, read, update, delete employee records
- **Department Management** - Organize employees by departments
- **Leave Requests** - Submit, approve, and track employee leave requests
- **PostgreSQL Database** - Reliable data persistence
- **RESTful API** - Well-documented FastAPI endpoints
- **Modern UI** - Responsive React frontend
- **Docker Support** - Easy deployment with docker-compose

## 📖 Documentation

- [QUICKSTART.md](QUICKSTART.md) - Quick reference and common commands
- [README-DOCKER.md](README-DOCKER.md) - Complete Docker deployment guide
- [AWS-EC2-DEPLOYMENT.md](AWS-EC2-DEPLOYMENT.md) - Step-by-step AWS EC2 deployment

## 🔗 Useful Links

After starting the application:
- **Frontend:** http://localhost
- **API Docs:** http://localhost/docs
- **API ReDoc:** http://localhost/redoc
- **Health Check:** http://localhost/health
- `DATABASE_URL` - PostgreSQL connection string
- `ENVIRONMENT` - dev, test, staging, or prod
- `REACT_APP_API_URL` - API endpoint URL

## API Endpoints

- `/` - Welcome endpoint
- `/health` - Health check
- `/docs` - Swagger API documentation
- `/api/v1/employees/` - Employee management
- `/api/v1/departments/` - Department management
- `/api/v1/leaves/` - Leave request management

## Features

- ✅ Employee CRUD operations
- ✅ Department management
- ✅ Leave request tracking
- ✅ PostgreSQL database
- ✅ RESTful API
- ✅ Interactive API documentation
- ✅ Health checks
- ✅ CORS support
