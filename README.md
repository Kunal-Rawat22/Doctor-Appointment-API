# 🏥 Doctor Appointment API

A FastAPI-based REST API for managing doctor appointments with JWT authentication and Role-Based Access Control (RBAC).

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Setup Instructions](#setup-instructions)
- [Authentication & RBAC](#authentication--role-based-access-control-rbac)
- [API Endpoints](#api-endpoints)
- [Usage Examples](#usage-examples)

## ✨ Features

- 🔐 JWT-based authentication
- 🛂 Role-Based Access Control (RBAC)
- 👨‍⚕️ Doctor availability management
- 📅 Appointment booking and management
- 🗄️ MySQL database with async SQLAlchemy
- 🐳 Docker containerization
- 📚 Interactive API documentation (Swagger UI)

## 🛠 Tech Stack

- **Framework**: FastAPI
- **Database**: MySQL 8.0
- **ORM**: SQLAlchemy (Async)
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt (passlib)
- **Containerization**: Docker & Docker Compose

## 🚀 Setup Instructions

### Prerequisites

- Docker and Docker Compose installed
- Git (optional, for cloning)

### Quick Start with Docker Compose

1. **Clone the repository** (if applicable):
   ```bash
   git clone <repository-url>
   cd Doctor-Appointment-API
   ```

2. **Create a `.env` file** in the root directory:
   ```env
   DATABASE_URL=mysql+aiomysql://fastapi:fastapi@mysql:3306/fastapi_db
   SECRET_KEY=your-secret-key-here-change-in-production
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

   > ⚠️ **Important**: Change `SECRET_KEY` to a strong, random value in production!

3. **Start the services**:
   ```bash
   docker-compose up --build
   ```

   This will:
   - Build the FastAPI application container
   - Start MySQL database container
   - Wait for MySQL to be healthy before starting the API
   - Expose the API on `http://localhost:8000`

4. **Access the API**:
   - **API**: http://localhost:8000
   - **Swagger UI**: http://localhost:8000/docs
   - **ReDoc**: http://localhost:8000/redoc
   - **MySQL**: localhost:3306

### Manual Setup (Without Docker)

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up MySQL database**:
   - Create a database named `fastapi_db`
   - Update `DATABASE_URL` in `.env` to point to your MySQL instance

3. **Run the application**:
   ```bash
   uvicorn app.main:app --reload
   ```

## 🔐 Authentication & Role-Based Access Control (RBAC)

This project uses JWT-based authentication combined with role-based authorization to protect APIs.

### 🔑 Authentication Flow (JWT)

#### 1️⃣ User Registration
**POST** `/auth/register`

Creates a new user with a role:
- `DOCTOR`
- `PATIENT`

Password is:
- ✅ hashed using bcrypt
- ✅ never stored in plain text

**Request Body**:
```json
{
  "email": "doctor@example.com",
  "password": "securepassword",
  "role": "doctor",
  "name": "Dr. John Doe"
}
```

#### 2️⃣ Login
**POST** `/auth/login`

Returns a JWT token:

**Request** (form-data):
```
username: doctor@example.com
password: securepassword
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

#### 3️⃣ Using the Token

All protected APIs require:
```
Authorization: Bearer <your_token>
```

**In Swagger UI**:
1. Click **Authorize** button
2. Paste token (without "Bearer" prefix)
3. Click **Authorize**
4. Done ✅

### 🔐 JWT Token Structure

```json
{
  "sub": "user_email",
  "exp": 1700000000
}
```

| Field | Description |
|-------|-------------|
| `sub` | User email (subject) |
| `exp` | Token expiry timestamp |

### 🛂 Role-Based Access Control (RBAC)

RBAC is implemented using FastAPI dependencies.

#### Role Enum

```python
class UserRole(str, Enum):
    DOCTOR = "doctor"
    PATIENT = "patient"
```

#### Role Guard

```python
def require_role(*roles: UserRole):
    async def role_checker(user=Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(
                status_code=403,
                detail="Access denied"
            )
        return user
    return role_checker
```

### 🧠 How Authorization Works

1. Token is extracted from request header (`Authorization: Bearer <token>`)
2. Token is decoded and validated
3. User is fetched from database using email from token
4. Role is validated against endpoint requirements
5. Request is allowed or rejected (403 Forbidden)

### 📌 API Access Rules

#### ✅ Public Routes

| Endpoint | Access |
|----------|--------|
| `POST /auth/register` | Public |
| `POST /auth/login` | Public |
| `PUT /auth/forget-password` | Public |

#### 👨‍⚕️ Doctor-Only APIs

| Endpoint | Description | Protection |
|----------|-------------|------------|
| `POST /doctors/availabilty` | Set availability | `Depends(roles.require_role(UserRole.DOCTOR))` |
| `GET /appointments/doctor/{doctor_id}` | View doctor appointments | `Depends(roles.require_role(UserRole.DOCTOR))` |

#### 🧑‍⚕️ Patient-Only APIs

| Endpoint | Description | Protection |
|----------|-------------|------------|
| `POST /appointments` | Book appointment | `Depends(roles.require_role(UserRole.PATIENT))` |
| `GET /appointments/patient/{patient_id}` | View patient appointments | `Depends(roles.require_role(UserRole.PATIENT))` |
| `DELETE /appointments/cancel/{appointment_id}` | Cancel appointment | `Depends(roles.require_role(UserRole.PATIENT))` |

#### 🔓 Authenticated (Any Role)

| Endpoint | Description | Protection |
|----------|-------------|------------|
| `GET /doctors` | List all doctors | `Depends(auth.get_current_user)` |
| `GET /doctors/{doctor_id}/availabilty` | Get doctor availability | `Depends(auth.get_current_user)` |

### 🔍 Example: Protected Endpoint

```python
@router.post("/appointments")
async def create_appointment(
    data: AppointmentRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(roles.require_role(UserRole.PATIENT))
):
    return await appointment_service.create_appointment(data, db)
```

- ✅ Only patients can access
- ❌ Doctors will get `403 Forbidden`

## 📡 API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/register` | Register new user | ❌ |
| POST | `/auth/login` | Login and get JWT token | ❌ |
| PUT | `/auth/forget-password` | Reset password | ❌ |

### Doctors

| Method | Endpoint | Description | Auth Required | Role Required |
|--------|----------|-------------|---------------|---------------|
| GET | `/doctors` | List all doctors | ✅ | Any |
| GET | `/doctors/{doctor_id}/availabilty` | Get doctor availability | ✅ | Any |
| POST | `/doctors/availabilty` | Set doctor availability | ✅ | Doctor |

### Appointments

| Method | Endpoint | Description | Auth Required | Role Required |
|--------|----------|-------------|---------------|---------------|
| POST | `/appointments` | Book appointment | ✅ | Patient |
| GET | `/appointments/doctor/{doctor_id}` | Get doctor appointments | ✅ | Doctor |
| GET | `/appointments/patient/{patient_id}` | Get patient appointments | ✅ | Patient |
| DELETE | `/appointments/cancel/{appointment_id}` | Cancel appointment | ✅ | Patient |

## 💡 Usage Examples

### 1. Register a Doctor

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "doctor@example.com",
    "password": "securepassword123",
    "role": "doctor",
    "name": "Dr. Jane Smith"
  }'
```

### 2. Register a Patient

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "patient@example.com",
    "password": "securepassword123",
    "role": "patient",
    "name": "John Doe"
  }'
```

### 3. Login

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=doctor@example.com&password=securepassword123"
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 4. Set Doctor Availability (Doctor Only)

```bash
curl -X POST "http://localhost:8000/doctors/availabilty" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "doctor_id": 1,
    "start_time": "2024-01-15T09:00:00",
    "end_time": "2024-01-15T17:00:00"
  }'
```

### 5. Book Appointment (Patient Only)

```bash
curl -X POST "http://localhost:8000/appointments" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "doctor_id": 1,
    "appointment_time": "2024-01-15T10:00:00",
    "patient_id": 2
  }'
```

### 6. View Appointments (Role-Specific)

**As Doctor**:
```bash
curl -X GET "http://localhost:8000/appointments/doctor/1" \
  -H "Authorization: Bearer DOCTOR_TOKEN_HERE"
```

**As Patient**:
```bash
curl -X GET "http://localhost:8000/appointments/patient/2" \
  -H "Authorization: Bearer PATIENT_TOKEN_HERE"
```

## 🧪 Testing

Run tests with:
```bash
pytest
```

## 📝 Environment Variables

Create a `.env` file with the following variables:

```env
# Database
DATABASE_URL=mysql+aiomysql://fastapi:fastapi@mysql:3306/fastapi_db

# JWT Configuration
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 🐳 Docker Services

- **API Service**: FastAPI application (port 8000)
- **MySQL Service**: Database (port 3306)
  - Database: `fastapi_db`
  - User: `fastapi`
  - Password: `fastapi`
  - Root Password: `root`

## 📚 Additional Resources

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔒 Security Notes

- ⚠️ Always use HTTPS in production
- ⚠️ Change default database passwords
- ⚠️ Use a strong, random `SECRET_KEY`
- ⚠️ Set appropriate token expiration times
- ⚠️ Never commit `.env` files to version control