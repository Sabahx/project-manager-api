# Frontend Integration Guide

This guide helps frontend developers integrate with the Project Manager API.

## Getting Started

### 1. Base URL
```javascript
const API_BASE_URL = 'http://localhost:8000/api';
```

### 2. Authentication Setup

```javascript
// Login and store tokens
async function login(username, password) {
  const response = await fetch('http://localhost:8000/api/token/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });

  const data = await response.json();
  localStorage.setItem('access_token', data.access);
  localStorage.setItem('refresh_token', data.refresh);
  return data;
}

// Add auth header to requests
function getAuthHeaders() {
  const token = localStorage.getItem('access_token');
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  };
}

// Refresh token when expired
async function refreshToken() {
  const refresh = localStorage.getItem('refresh_token');
  const response = await fetch('http://localhost:8000/api/token/refresh/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh })
  });

  const data = await response.json();
  localStorage.setItem('access_token', data.access);
  return data.access;
}
```

## API Examples

### User Registration

```javascript
async function register(username, email, password) {
  const response = await fetch(`${API_BASE_URL}/register/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, email, password })
  });
  return response.json();
}
```

### Projects

```javascript
// Get all projects
async function getProjects() {
  const response = await fetch(`${API_BASE_URL}/projects/`, {
    headers: getAuthHeaders()
  });
  return response.json();
}

// Create project
async function createProject(name, description) {
  const response = await fetch(`${API_BASE_URL}/projects/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ name, description })
  });
  return response.json();
}

// Get project details
async function getProject(id) {
  const response = await fetch(`${API_BASE_URL}/projects/${id}/`, {
    headers: getAuthHeaders()
  });
  return response.json();
}

// Update project
async function updateProject(id, data) {
  const response = await fetch(`${API_BASE_URL}/projects/${id}/`, {
    method: 'PATCH',
    headers: getAuthHeaders(),
    body: JSON.stringify(data)
  });
  return response.json();
}

// Delete project
async function deleteProject(id) {
  const response = await fetch(`${API_BASE_URL}/projects/${id}/`, {
    method: 'DELETE',
    headers: getAuthHeaders()
  });
  return response.ok;
}
```

### Tasks

```javascript
// Get all tasks with filters
async function getTasks(filters = {}) {
  const params = new URLSearchParams(filters);
  const response = await fetch(`${API_BASE_URL}/tasks/?${params}`, {
    headers: getAuthHeaders()
  });
  return response.json();
}

// Examples of filters:
// getTasks({ status: 'todo' })
// getTasks({ project: 1, status: 'in_progress' })
// getTasks({ search: 'bug fix' })
// getTasks({ ordering: '-created_at' })

// Create task
async function createTask(taskData) {
  const response = await fetch(`${API_BASE_URL}/tasks/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(taskData)
  });
  return response.json();
}

// Update task
async function updateTask(id, updates) {
  const response = await fetch(`${API_BASE_URL}/tasks/${id}/`, {
    method: 'PATCH',
    headers: getAuthHeaders(),
    body: JSON.stringify(updates)
  });
  return response.json();
}

// Follow/Unfollow task
async function followTask(id) {
  const response = await fetch(`${API_BASE_URL}/tasks/${id}/follow/`, {
    method: 'POST',
    headers: getAuthHeaders()
  });
  return response.json();
}

async function unfollowTask(id) {
  const response = await fetch(`${API_BASE_URL}/tasks/${id}/unfollow/`, {
    method: 'POST',
    headers: getAuthHeaders()
  });
  return response.json();
}
```

### Comments

```javascript
// Get comments for a task
async function getComments(taskId) {
  const response = await fetch(`${API_BASE_URL}/comments/?task=${taskId}`, {
    headers: getAuthHeaders()
  });
  return response.json();
}

// Create comment
async function createComment(taskId, content) {
  const response = await fetch(`${API_BASE_URL}/comments/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ task: taskId, content })
  });
  return response.json();
}
```

### Notifications

```javascript
// Get all notifications
async function getNotifications() {
  const response = await fetch(`${API_BASE_URL}/notifications/`, {
    headers: getAuthHeaders()
  });
  return response.json();
}

// Mark notification as read
async function markAsRead(id) {
  const response = await fetch(`${API_BASE_URL}/notifications/${id}/mark-as-read/`, {
    method: 'POST',
    headers: getAuthHeaders()
  });
  return response.json();
}
```

### Activity Logs

```javascript
// Get task history
async function getTaskLogs(taskId) {
  const response = await fetch(`${API_BASE_URL}/logs/${taskId}/`, {
    headers: getAuthHeaders()
  });
  return response.json();
}
```

## React Example

```jsx
import { useState, useEffect } from 'react';

function ProjectList() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchProjects() {
      try {
        const token = localStorage.getItem('access_token');
        const response = await fetch('http://localhost:8000/api/projects/', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        const data = await response.json();
        setProjects(data.results); // Paginated response
        setLoading(false);
      } catch (error) {
        console.error('Error fetching projects:', error);
        setLoading(false);
      }
    }

    fetchProjects();
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      {projects.map(project => (
        <div key={project.id}>
          <h3>{project.name}</h3>
          <p>{project.description}</p>
          <p>Tasks: {project.task_count}</p>
          <p>Members: {project.member_count}</p>
        </div>
      ))}
    </div>
  );
}
```

## Response Format

### Successful Response
```json
{
  "count": 10,
  "next": "http://localhost:8000/api/projects/?page=2",
  "previous": null,
  "results": [...]
}
```

### Error Response
```json
{
  "error": true,
  "status_code": 400,
  "message": "Error message",
  "details": {...}
}
```

## Data Models

### Project
```typescript
interface Project {
  id: number;
  name: string;
  description: string;
  manager: User;
  task_count: number;
  member_count: number;
  created_at: string;
}
```

### Task
```typescript
interface Task {
  id: number;
  title: string;
  description: string;
  status: 'todo' | 'in_progress' | 'done';
  due_date: string | null;
  project: number;
  project_name: string;
  assigned_to: User;
  comment_count: number;
  follower_count: number;
  is_following: boolean;
  created_at: string;
}
```

### User
```typescript
interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
}
```

## Pagination

All list endpoints support pagination:
- `?page=2` - Get specific page
- `?page_size=50` - Change page size (default: 20)

## Filtering & Search

Tasks support advanced filtering:
- `?status=todo` - Filter by status
- `?project=1` - Filter by project
- `?assigned_to=2` - Filter by user
- `?search=bug` - Search in title/description
- `?ordering=-created_at` - Sort by field (- for descending)

## Testing the API

Run the test script:
```bash
python test_api.py
```

Or use the interactive API docs:
- http://localhost:8000/api/docs/ (Swagger UI)
- http://localhost:8000/api/redoc/ (ReDoc)

## Health Check

Check if API is running:
```javascript
fetch('http://localhost:8000/api/health/')
  .then(r => r.json())
  .then(data => console.log(data));
```

## CORS Configuration

The API is configured to allow requests from:
- http://localhost:3000
- http://localhost:3001

Update `.env` to add more origins:
```
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://yourapp.com
```
