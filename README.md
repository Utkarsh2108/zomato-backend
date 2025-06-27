# Zomato Clone Backend API

A comprehensive food delivery backend API built with FastAPI, featuring user authentication, restaurant management, order processing, reviews, and search functionality.

## 🚀 Features

- **User Authentication**: JWT-based authentication with role-based access control
- **Restaurant Management**: CRUD operations for restaurants with admin controls
- **Menu Management**: Dynamic menu items with categories and availability status
- **Order Processing**: Complete order lifecycle from placement to delivery
- **Reviews System**: Customer feedback and rating system
- **Favorites**: Personal restaurant favorites for users
- **Search & Filters**: Advanced search with multiple filter options
- **Admin Dashboard**: Administrative controls for managing the platform

## 🛠️ Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT (JSON Web Tokens)
- **Validation**: Pydantic models
- **Migrations**: Alembic
- **Documentation**: Auto-generated Swagger/OpenAPI docs

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL
- pip or conda

## 🔧 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/zomato-clone-backend.git
cd zomato-clone-backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=postgresql://username:password@localhost/databasename

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

### 5. Start the Application

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc


## 🔐 Authentication

The API uses JWT-based authentication. To access protected endpoints:

1. Register a new user or login with existing credentials
2. Use the returned access token in the Authorization header:
   ```
   Authorization: Bearer <your-token-here>
   ```

### User Roles

- **Customer** (default): Can browse restaurants, place orders, add reviews, manage favorites
- **Admin**: Full access including restaurant and menu management

## 📖 API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login

### Restaurants
- `GET /restaurants/` - List all restaurants
- `GET /restaurants/{id}` - Get restaurant details
- `POST /restaurants/` - Add restaurant (admin only)
- `PUT /restaurants/{id}` - Update restaurant (admin only)
- `DELETE /restaurants/{id}` - Delete restaurant (admin only)

### Menu Management
- `GET /restaurants/{id}/menu/` - Get restaurant menu
- `POST /restaurants/{id}/menu/` - Add menu item (admin only)
- `PUT /menu/{item_id}/` - Update menu item (admin only)
- `DELETE /menu/{item_id}/` - Delete menu item (admin only)

### Orders
- `POST /orders/` - Place an order
- `GET /orders/my/` - Get user's orders
- `GET /orders/{id}/` - Get order details
- `PUT /orders/{id}/cancel` - Cancel order
- `GET /admin/orders/` - Admin view of all orders

### Reviews
- `POST /reviews/` - Add review
- `GET /reviews/restaurant/{restaurant_id}/` - Get restaurant reviews

### Favorites
- `POST /favorites/{restaurant_id}/` - Toggle favorite
- `GET /favorites/` - List favorite restaurants

### Search & Filters
- `GET /search/?query=burger` - Search restaurants/dishes
- Filter parameters: `cuisine`, `rating`, `is_open`, `is_active`

