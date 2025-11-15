"""
Simple API testing script for frontend developers
Usage: python test_api.py
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_health_check():
    """Test health check endpoint"""
    print("\n=== Testing Health Check ===")
    response = requests.get(f"{BASE_URL}/health/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_register():
    """Test user registration"""
    print("\n=== Testing User Registration ===")
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    }
    response = requests.post(f"{BASE_URL}/register/", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 201

def test_login():
    """Test user login and get token"""
    print("\n=== Testing Login ===")
    data = {
        "username": "testuser",
        "password": "testpass123"
    }
    response = requests.post("http://localhost:8000/api/token/", json=data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        tokens = response.json()
        print(f"Access Token: {tokens['access'][:50]}...")
        print(f"Refresh Token: {tokens['refresh'][:50]}...")
        return tokens['access']
    else:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return None

def test_create_project(token):
    """Test project creation"""
    print("\n=== Testing Create Project ===")
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "name": "Test Project",
        "description": "This is a test project"
    }
    response = requests.post(f"{BASE_URL}/projects/", json=data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    if response.status_code == 201:
        return response.json()['id']
    return None

def test_list_projects(token):
    """Test listing projects"""
    print("\n=== Testing List Projects ===")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/projects/", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_create_task(token, project_id):
    """Test task creation"""
    print("\n=== Testing Create Task ===")
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "title": "Test Task",
        "description": "This is a test task",
        "status": "todo",
        "project": project_id,
        "due_date": "2025-12-31"
    }
    response = requests.post(f"{BASE_URL}/tasks/", json=data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    if response.status_code == 201:
        return response.json()['id']
    return None

def test_list_tasks(token):
    """Test listing tasks with filters"""
    print("\n=== Testing List Tasks ===")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/tasks/?status=todo", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def run_all_tests():
    """Run all API tests"""
    print("=" * 60)
    print("PROJECT MANAGER API TESTS")
    print("=" * 60)

    # Test health check
    if not test_health_check():
        print("\n❌ Health check failed! Make sure the server is running.")
        return

    # Test registration
    test_register()

    # Test login
    token = test_login()
    if not token:
        print("\n❌ Login failed! Cannot continue tests.")
        return

    # Test projects
    project_id = test_create_project(token)
    if project_id:
        test_list_projects(token)

        # Test tasks
        task_id = test_create_task(token, project_id)
        if task_id:
            test_list_tasks(token)

    print("\n" + "=" * 60)
    print("✅ API TESTS COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    try:
        run_all_tests()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to API server!")
        print("Make sure the server is running: python manage.py runserver")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
