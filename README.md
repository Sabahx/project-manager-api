# Project Manager API

A comprehensive Django REST Framework-based project management system with task tracking, real-time notifications, and team collaboration features.

## Features

- **Project Management**: Create and manage projects with team members
- **Task Tracking**: Full CRUD operations for tasks with status management (To Do, In Progress, Done)
- **Collaboration**: Comments, task followers, and real-time notifications
- **Audit Trail**: Complete task history logging with change tracking
- **Authentication**: JWT-based authentication with token refresh
- **Filtering & Search**: Advanced filtering, search, and ordering capabilities
- **API Documentation**: Interactive Swagger UI and ReDoc documentation
- **Security**: Role-based permissions and secure authentication

## Tech Stack

- **Backend**: Django 5.2 + Django REST Framework
- **Authentication**: JWT (Simple JWT)
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Documentation**: drf-spectacular (OpenAPI 3.0)
- **Security**: CORS headers, rate limiting ready

## Quick Start

### Prerequisites

- Python 3.10+
- pip
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd project_manager
```

2. **Create and activate virtual environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
# Copy the example env file
cp .env.example .env

# Edit .env with your settings
```

5. **Run migrations**
```bash
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Run development server**
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **Schema**: http://localhost:8000/api/schema/

## API Endpoints

### Authentication
- `POST /api/register/` - Register new user
- `POST /api/token/` - Obtain JWT token pair
- `POST /api/token/refresh/` - Refresh access token

### Projects
- `GET /api/projects/` - List user's projects
- `POST /api/projects/` - Create new project
- `GET /api/projects/{id}/` - Get project details
- `PUT/PATCH /api/projects/{id}/` - Update project
- `DELETE /api/projects/{id}/` - Delete project

### Tasks
- `GET /api/tasks/` - List tasks (with filters)
- `POST /api/tasks/` - Create new task
- `GET /api/tasks/{id}/` - Get task details
- `PUT/PATCH /api/tasks/{id}/` - Update task
- `DELETE /api/tasks/{id}/` - Delete task

**Task Filters**:
- `?status=todo|in_progress|done`
- `?assigned_to={user_id}`
- `?project={project_id}`
- `?search={keyword}`
- `?ordering=-created_at`

### Comments
- `GET /api/comments/` - List comments
- `POST /api/comments/` - Create comment
- `GET /api/comments/{id}/` - Get comment details
- `PUT/PATCH /api/comments/{id}/` - Update comment
- `DELETE /api/comments/{id}/` - Delete comment

### Notifications
- `GET /api/notifications/` - Get user notifications
- `POST /api/notifications/{id}/mark-as-read/` - Mark as read

### Task Following
- `POST /api/tasks/{id}/follow/` - Follow a task
- `POST /api/tasks/{id}/unfollow/` - Unfollow a task

### Activity Logs
- `GET /api/logs/{task_id}/` - Get task change history

## Usage Examples

### Register and Login

```bash
# Register
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "email": "john@example.com", "password": "securepass123"}'

# Get token
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "password": "securepass123"}'
```

### Create Project

```bash
curl -X POST http://localhost:8000/api/projects/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Project", "description": "Project description"}'
```

### Create Task

```bash
curl -X POST http://localhost:8000/api/tasks/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Implement feature X",
    "description": "Detailed description",
    "status": "todo",
    "project": 1,
    "due_date": "2025-12-31"
  }'
```

## Permissions

### Project Permissions
- **Manager**: Full control (create, update, delete)
- **Members**: Read-only access

### Task Permissions
- **Project Manager**: Full control over all tasks
- **Assigned User**: Can update their own tasks
- **Project Members**: Read-only access

### Comment Permissions
- **Author**: Can edit/delete own comments
- **Project Members**: Can create and read comments

## Data Models

### Project
- `name` - Project name
- `description` - Project description
- `manager` - Project manager (auto-set to creator)
- `members` - Project team members

### Task
- `title` - Task title
- `description` - Task description
- `status` - todo | in_progress | done
- `due_date` - Optional deadline
- `project` - Related project
- `assigned_to` - Assigned user

### Comment
- `content` - Comment text
- `task` - Related task
- `author` - Comment author

### Notification
- `message` - Notification message
- `task` - Related task (optional)
- `comment` - Related comment (optional)
- `is_read` - Read status

## Development

### Running Tests

```bash
python manage.py test
```

### Code Formatting

```bash
black .
flake8
```

### Database Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

## Deployment

### Environment Variables for Production

Update your `.env` file:

```env
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com

# PostgreSQL
DB_ENGINE=django.db.backends.postgresql
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
```

### Using Gunicorn

```bash
gunicorn project_manager.wsgi:application --bind 0.0.0.0:8000
```

## Frontend Integration

This API is designed to work with any frontend framework. Example with fetch:

```javascript
// Login
const response = await fetch('http://localhost:8000/api/token/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'john', password: 'pass123' })
});
const { access, refresh } = await response.json();

// Use token for authenticated requests
const projects = await fetch('http://localhost:8000/api/projects/', {
  headers: { 'Authorization': `Bearer ${access}` }
});
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is open source and available under the MIT License.

## Support

For issues and questions, please open an issue on GitHub.

## Roadmap

- [ ] Email notifications
- [ ] File attachments for tasks
- [ ] Task priorities
- [ ] Project templates
- [ ] User profiles with avatars
- [ ] Activity dashboard
- [ ] WebSocket support for real-time updates
- [ ] Mobile app support
