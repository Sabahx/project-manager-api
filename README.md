# 🗂️ Project Manager API

A complete RESTful API system for managing Projects and Tasks using Django REST Framework with JWT authentication and role-based permissions.

---

## ⚙️ How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Run the server
python manage.py runserver
```

---

## 🔐 JWT Authentication

### 1. Obtain Token:
```http
POST /api/token/
{
  "username": "your_username",
  "password": "your_password"
}
```

### 2. Refresh Token:
```http
POST /api/token/refresh/
{
  "refresh": "your_refresh_token"
}
```

---

## 🧩 API Endpoints

### 📁 Projects

| Method | Endpoint                  | Description             | Access                 |
|--------|---------------------------|-------------------------|------------------------|
| GET    | `/api/projects/`          | List joined projects    | Authenticated members  |
| POST   | `/api/projects/`          | Create a new project    | Any authenticated user |
| PATCH  | `/api/projects/<id>/`     | Update a project        | Project manager only   |
| DELETE | `/api/projects/<id>/`     | Delete a project        | Project manager only   |

### ✅ Tasks

| Method | Endpoint                  | Description               | Access                                 |
|--------|---------------------------|---------------------------|----------------------------------------|
| GET    | `/api/tasks/`             | List tasks                | Project members                        |
| POST   | `/api/tasks/`             | Create a new task         | Project manager only                   |
| PATCH  | `/api/tasks/<id>/`        | Update a task             | Project manager or assigned user       |
| DELETE | `/api/tasks/<id>/`        | Delete a task             | Project manager only                   |

---

## 🔍 Filtering and Search

You can filter tasks by:

- `status` (`todo`, `in_progress`, `done`)
- `due_date`
- `assigned_to`
- `project`

Example:

```http
GET /api/tasks/?status=todo&assigned_to=2&project=1&due_date=2025-06-01
```

And search by title or description:

```http
GET /api/tasks/?search=delivery
```

---

## 🧪 Run Tests

```bash
python manage.py test
```

---

## 🧰 Tech Stack

- Django
- Django REST Framework
- Simple JWT
- Django Filters

---

## 📬 Author

[Sabahx on GitHub](https://github.com/Sabahx)
