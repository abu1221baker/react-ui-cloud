# E-Commerce API with Django REST Framework

A complete e-commerce REST API built with Django and Django REST Framework, featuring JWT authentication and comprehensive product and order management.

## Features

- ✅ JWT Token-based Authentication
- ✅ User Registration & Login
- ✅ Product Management (CRUD operations)
- ✅ Order Management
- ✅ Stock Management
- ✅ Function-based Views
- ✅ Admin Panel

## Tech Stack

### Core
- Django 4.2.7
- Django REST Framework 3.14.0
- SimpleJWT 5.3.0
- CORS Headers 4.3.0

### Production
- Gunicorn 21.2.0 (WSGI server)
- PostgreSQL (via psycopg2-binary 2.9.9)
- WhiteNoise 6.6.0 (static file serving)
- python-decouple 3.8 (environment variables)
- dj-database-url 2.1.0 (database configuration)

## Installation

### Prerequisites

- Python 3.8+
- pip

### Setup Instructions

#### Local Development

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd "react ui cloud"
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your settings (optional for local development)
   ```

5. **Run migrations**:
   ```bash
   python3 manage.py migrate
   ```

6. **Create a superuser** (for admin access):
   ```bash
   python3 manage.py createsuperuser
   ```

7. **Run the development server**:
   ```bash
   python3 manage.py runserver
   ```

The API will be available at `http://localhost:8000/`

#### Production Deployment (Render)

1. **Push your code to GitHub** (or GitLab/Bitbucket)

2. **Create a new Web Service on Render**:
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect your repository
   - Configure the service:
     - **Name**: Your app name
     - **Environment**: Python 3
     - **Build Command**: `./build.sh`
     - **Start Command**: `gunicorn ecommerce_api.wsgi:application`

3. **Add a PostgreSQL Database**:
   - In Render Dashboard, click "New +" → "PostgreSQL"
   - Copy the Internal Database URL

4. **Set Environment Variables** in your Web Service:
   - `SECRET_KEY`: Generate a secure key (use `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
   - `DATABASE_URL`: Paste the PostgreSQL Internal Database URL
   - `ALLOWED_HOSTS`: Your Render app URL (e.g., `your-app.onrender.com`)
   - `DEBUG`: `False`
   - `CORS_ALLOWED_ORIGINS`: Your frontend URL (e.g., `https://yourfrontend.com`)

5. **Deploy**: Render will automatically build and deploy your app

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/accounts/register/` | Register a new user | No |
| POST | `/api/accounts/login/` | Login and get JWT tokens | No |
| GET | `/api/accounts/profile/` | Get user profile | Yes |
| POST | `/api/accounts/token/refresh/` | Refresh access token | No |

### Products

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/products/` | List all products | No |
| POST | `/api/products/` | Create a new product | Yes |
| GET | `/api/products/{id}/` | Get product details | No |
| PUT | `/api/products/{id}/` | Update a product | Yes |
| DELETE | `/api/products/{id}/` | Delete a product | Yes |

**Query Parameters for Product List:**
- `category`: Filter by category (e.g., `electronics`, `clothing`)
- `search`: Search products by name

### Orders

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/orders/` | List user's orders | Yes |
| POST | `/api/orders/` | Create a new order | Yes |
| GET | `/api/orders/{id}/` | Get order details | Yes |
| PUT | `/api/orders/{id}/` | Update order status | Yes |

## API Usage Examples

### 1. Register a New User

```bash
curl -X POST http://localhost:8000/api/accounts/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "securepass123",
    "password2": "securepass123",
    "first_name": "Test",
    "last_name": "User",
    "phone_number": "1234567890",
    "address": "123 Main St"
  }'
```

### 2. Login

```bash
curl -X POST http://localhost:8000/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "securepass123"
  }'
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User"
  },
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 3. Create a Product (Authenticated)

```bash
curl -X POST http://localhost:8000/api/products/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "name": "Laptop",
    "description": "High-performance laptop",
    "price": "999.99",
    "stock": 50,
    "category": "electronics"
  }'
```

### 4. List All Products

```bash
curl http://localhost:8000/api/products/
```

### 5. Create an Order (Authenticated)

```bash
curl -X POST http://localhost:8000/api/orders/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "items": [
      {
        "product_id": 1,
        "quantity": 2
      }
    ],
    "shipping_address": "123 Main St, City, Country",
    "payment_method": "card"
  }'
```

### 6. Get User's Orders (Authenticated)

```bash
curl http://localhost:8000/api/orders/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Project Structure

```
react ui cloud/
├── ecommerce_api/          # Django project configuration
│   ├── settings.py         # Project settings (with production config)
│   ├── urls.py            # Main URL configuration
│   ├── wsgi.py            # WSGI configuration
│   └── asgi.py
├── accounts/              # User authentication app
│   ├── models.py         # Custom User model
│   ├── serializers.py    # User serializers
│   ├── views.py          # Auth views (register, login)
│   └── urls.py
├── products/             # Products management app
│   ├── models.py        # Product model
│   ├── serializers.py   # Product serializers
│   ├── views.py         # Product CRUD views
│   └── urls.py
├── orders/              # Orders management app
│   ├── models.py       # Order and OrderItem models
│   ├── serializers.py  # Order serializers
│   ├── views.py        # Order management views
│   └── urls.py
├── manage.py            # Django management script
├── requirements.txt     # Python dependencies
├── build.sh            # Render build script
├── .env.example        # Environment variables template
├── .gitignore          # Git ignore file
└── README.md
```

## Models

### User Model
- username, email, password (default Django fields)
- phone_number
- address

### Product Model
- name, description
- price, stock
- category (electronics, clothing, food, books, home, sports, toys, other)
- image (optional)
- is_active, created_at, updated_at

### Order Model
- user (ForeignKey)
- total_amount
- status (pending, processing, shipped, delivered, cancelled)
- shipping_address
- payment_method (cod, card, upi, wallet)
- created_at, updated_at

### OrderItem Model
- order (ForeignKey)
- product (ForeignKey)
- quantity, price

## Authentication

This API uses JWT (JSON Web Tokens) for authentication. After logging in, you'll receive two tokens:

- **Access Token**: Short-lived token (1 day) used for API requests
- **Refresh Token**: Long-lived token (7 days) used to get new access tokens

Include the access token in the Authorization header:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## Admin Panel

Access the Django admin panel at `http://localhost:8000/admin/` using your superuser credentials.

From the admin panel, you can:
- Manage users
- Create/edit/delete products
- View and manage orders
- Monitor order items

## Features Explained

### Stock Management
- When an order is created, product stock is automatically decreased
- Orders are validated to ensure sufficient stock before creation

### Order Management
- Users can only view their own orders
- Orders include detailed item information
- Total amount is automatically calculated based on product prices

### Product Filtering
- Filter products by category
- Search products by name
- Only active products are shown to non-authenticated users

## Environment Variables

The application uses environment variables for configuration. Create a `.env` file based on `.env.example`:

- `SECRET_KEY`: Django secret key (required in production)
- `DEBUG`: Set to `False` in production (default: False)
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `DATABASE_URL`: PostgreSQL connection string (optional, uses SQLite if not set)
- `CORS_ALLOWED_ORIGINS`: Comma-separated list of allowed CORS origins (optional)

## Production Configuration

The project is configured for production deployment with:

- ✅ Environment-based configuration using python-decouple
- ✅ PostgreSQL support (falls back to SQLite for local development)
- ✅ WhiteNoise for efficient static file serving
- ✅ Gunicorn as production WSGI server
- ✅ Secure settings (DEBUG=False, restricted CORS, etc.)
- ✅ Automated build script for Render deployment

## License

This project is open source and available under the MIT License.
