# ECOMMERCE API

A RESTful e-commerce API built with FastAPI, PostgreSQL, and SQLAlchemy.

## Features
- JWT Authentication
- Products catalog with pagination and filtering
- Cart management
- Order checkout with atomic transactions
- SMS notifications on order placement

## Requirements
- Python 3.12+
- PostgreSQL

## Setup

### 1. Clone the repo
```bash
git clone <repo-url>
cd into the repo
```

### 2. Create and activate virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp app/.env.example app/.env
```
Edit `app/.env` with your values:
```bash
DATABASE_URL=postgresql://myuser:mypassword@localhost/mydatabase
SECRET_KEY=your-secret-key-here
```

### 5. Create the database
```bash
sudo -u postgres psql
CREATE USER myuser WITH PASSWORD 'mypassword';
CREATE DATABASE mydatabase OWNER myuser;
\q
```

### 6. Run the app
```bash
fastapi dev app/main.py
```

API is available at `http://127.0.0.1:8000`  
Swagger docs at `http://127.0.0.1:8000/docs`

## API Endpoints

| Method | Route | Auth | Description |
|---|---|---|---|
| POST | `/auth/register` | ❌ | Register new user |
| POST | `/auth/login` | ❌ | Login and get token |
| GET | `/me` | ✅ | Get current user profile |
| GET | `/products` | ❌ | List products (paginated) |
| GET | `/products/{id}` | ❌ | Get single product |
| POST | `/cart` | ✅ | Add item to cart |
| GET | `/cart` | ✅ | Get cart |
| PATCH | `/cart/{id}` | ✅ | Update cart item quantity |
| DELETE | `/cart/{id}` | ✅ | Remove cart item |
| DELETE | `/cart` | ✅ | Clear cart |
| POST | `/orders/checkout` | ✅ | Place order |
| GET | `/orders` | ✅ | Get order history |
| GET | `/orders/{id}` | ✅ | Get single order |