import pytest
import json
from app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestHealth:
    """Test health check endpoint"""
    
    def test_health_check(self, client):
        """Test that health endpoint returns 200"""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data


class TestUsers:
    """Test user management endpoints"""
    
    def test_create_user(self, client):
        """Test creating a new user"""
        payload = {
            'name': 'John Doe',
            'email': 'john@example.com'
        }
        response = client.post('/users', 
                              data=json.dumps(payload),
                              content_type='application/json')
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['name'] == 'John Doe'
        assert data['email'] == 'john@example.com'
        assert 'id' in data
        assert 'created_at' in data
    
    def test_create_user_missing_name(self, client):
        """Test creating a user without name"""
        payload = {'email': 'john@example.com'}
        response = client.post('/users',
                              data=json.dumps(payload),
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_create_user_missing_email(self, client):
        """Test creating a user without email"""
        payload = {'name': 'John Doe'}
        response = client.post('/users',
                              data=json.dumps(payload),
                              content_type='application/json')
        assert response.status_code == 400
    
    def test_get_users(self, client):
        """Test getting all users"""
        # Create a user first
        payload = {'name': 'Jane Doe', 'email': 'jane@example.com'}
        client.post('/users', data=json.dumps(payload), content_type='application/json')
        
        # Get all users
        response = client.get('/users')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_get_user_by_id(self, client):
        """Test getting a specific user"""
        # Create a user
        payload = {'name': 'Alice', 'email': 'alice@example.com'}
        create_response = client.post('/users',
                                     data=json.dumps(payload),
                                     content_type='application/json')
        user_id = json.loads(create_response.data)['id']
        
        # Get the user
        response = client.get(f'/users/{user_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == user_id
        assert data['name'] == 'Alice'
    
    def test_get_user_not_found(self, client):
        """Test getting a non-existent user"""
        response = client.get('/users/invalid-id')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_update_user(self, client):
        """Test updating a user"""
        # Create a user
        payload = {'name': 'Bob', 'email': 'bob@example.com'}
        create_response = client.post('/users',
                                     data=json.dumps(payload),
                                     content_type='application/json')
        user_id = json.loads(create_response.data)['id']
        
        # Update the user
        update_payload = {'name': 'Robert'}
        response = client.put(f'/users/{user_id}',
                            data=json.dumps(update_payload),
                            content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['name'] == 'Robert'
        assert 'updated_at' in data
    
    def test_delete_user(self, client):
        """Test deleting a user"""
        # Create a user
        payload = {'name': 'Charlie', 'email': 'charlie@example.com'}
        create_response = client.post('/users',
                                     data=json.dumps(payload),
                                     content_type='application/json')
        user_id = json.loads(create_response.data)['id']
        
        # Delete the user
        response = client.delete(f'/users/{user_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'message' in data
        
        # Verify user is deleted
        get_response = client.get(f'/users/{user_id}')
        assert get_response.status_code == 404


class TestTasks:
    """Test task management endpoints"""
    
    def test_create_task(self, client):
        """Test creating a new task"""
        payload = {
            'title': 'Buy groceries',
            'description': 'Get milk and eggs',
            'status': 'pending'
        }
        response = client.post('/tasks',
                              data=json.dumps(payload),
                              content_type='application/json')
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['title'] == 'Buy groceries'
        assert data['status'] == 'pending'
        assert 'id' in data
    
    def test_create_task_missing_title(self, client):
        """Test creating a task without title"""
        payload = {'status': 'pending'}
        response = client.post('/tasks',
                              data=json.dumps(payload),
                              content_type='application/json')
        assert response.status_code == 400
    
    def test_get_tasks(self, client):
        """Test getting all tasks"""
        payload = {'title': 'Test task'}
        client.post('/tasks', data=json.dumps(payload), content_type='application/json')
        
        response = client.get('/tasks')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
    
    def test_get_tasks_by_status(self, client):
        """Test filtering tasks by status"""
        # Create tasks with different statuses
        task1 = {'title': 'Task 1', 'status': 'pending'}
        task2 = {'title': 'Task 2', 'status': 'completed'}
        
        client.post('/tasks', data=json.dumps(task1), content_type='application/json')
        client.post('/tasks', data=json.dumps(task2), content_type='application/json')
        
        # Get pending tasks
        response = client.get('/tasks?status=pending')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert all(task['status'] == 'pending' for task in data)
    
    def test_get_task_by_id(self, client):
        """Test getting a specific task"""
        payload = {'title': 'Important task'}
        create_response = client.post('/tasks',
                                     data=json.dumps(payload),
                                     content_type='application/json')
        task_id = json.loads(create_response.data)['id']
        
        response = client.get(f'/tasks/{task_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == task_id
    
    def test_get_task_not_found(self, client):
        """Test getting a non-existent task"""
        response = client.get('/tasks/invalid-id')
        assert response.status_code == 404
    
    def test_update_task(self, client):
        """Test updating a task"""
        payload = {'title': 'Original title', 'status': 'pending'}
        create_response = client.post('/tasks',
                                     data=json.dumps(payload),
                                     content_type='application/json')
        task_id = json.loads(create_response.data)['id']
        
        update_payload = {'status': 'completed'}
        response = client.put(f'/tasks/{task_id}',
                            data=json.dumps(update_payload),
                            content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'completed'
    
    def test_delete_task(self, client):
        """Test deleting a task"""
        payload = {'title': 'Task to delete'}
        create_response = client.post('/tasks',
                                     data=json.dumps(payload),
                                     content_type='application/json')
        task_id = json.loads(create_response.data)['id']
        
        response = client.delete(f'/tasks/{task_id}')
        assert response.status_code == 200
        
        # Verify task is deleted
        get_response = client.get(f'/tasks/{task_id}')
        assert get_response.status_code == 404


class TestErrorHandlers:
    """Test error handling"""
    
    def test_404_endpoint_not_found(self, client):
        """Test 404 error handler"""
        response = client.get('/nonexistent')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_405_method_not_allowed(self, client):
        """Test 405 error handler"""
        response = client.post('/health')  # GET only endpoint
        assert response.status_code == 405