# 🗂️ Project Manager API

A Django REST Framework–based backend for a Task & Project Management System.

This backend provides powerful features like project tracking, task management, task following, comment system, and change logs — all protected with JWT authentication.

---

## ✅ Features

- User Registration & JWT Login
- Project & Task CRUD operations
- Task Following
- Comment System
- Notification System
- Task Change Logs
- Comprehensive Test Coverage

---

## 🧪 Testing

All core functionalities are covered with unit and integration tests using Django’s test framework.  
To run the tests:

```bash
python manage.py test
✔️ Tests include:

User registration and login

Project and task creation

Following/unfollowing tasks

Comment permissions

Notification behavior

Task update logging and access control

🛠️ Tech Stack
Backend: Django, Django REST Framework

Auth: JWT (SimpleJWT)

Database: SQLite (default, switchable)

Tests: Built-in Django test client

🚀 Getting Started
bash
Copy
Edit
git clone https://github.com/Sabahx/project-manager-api.git
cd project-manager-api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
