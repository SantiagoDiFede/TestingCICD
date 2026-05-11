from flask import Flask, request, jsonify
from datetime import datetime
import uuid

app = Flask(__name__)

# In-memory storage for demo purposes
tasks = {}
users = {}

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    }), 200


# ============================================================================
# USER ENDPOINTS
# ============================================================================

@app.route('/users', methods=['POST'])
def create_user():
    """Create a new user"""
    data = request.get_json()
    
    if not data or 'name' not in data or 'email' not in data:
        return jsonify({'error': 'name and email are required'}), 400
    
    user_id = str(uuid.uuid4())
    user = {
        'id': user_id,
        'name': data['name'],
        'email': data['email'],
        'created_at': datetime.utcnow().isoformat()
    }
    
    users[user_id] = user
    return jsonify(user), 201


@app.route('/users', methods=['GET'])
def get_users():
    """Get all users"""
    return jsonify(list(users.values())), 200


@app.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get a specific user by ID"""
    if user_id not in users:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(users[user_id]), 200


@app.route('/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    """Update a user"""
    if user_id not in users:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    if 'name' in data:
        users[user_id]['name'] = data['name']
    if 'email' in data:
        users[user_id]['email'] = data['email']
    
    users[user_id]['updated_at'] = datetime.utcnow().isoformat()
    
    return jsonify(users[user_id]), 200


@app.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user"""
    if user_id not in users:
        return jsonify({'error': 'User not found'}), 404
    
    deleted_user = users.pop(user_id)
    return jsonify({'message': 'User deleted', 'user': deleted_user}), 200


# ============================================================================
# TASK ENDPOINTS
# ============================================================================

@app.route('/tasks', methods=['POST'])
def create_task():
    """Create a new task"""
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({'error': 'title is required'}), 400
    
    task_id = str(uuid.uuid4())
    task = {
        'id': task_id,
        'title': data['title'],
        'description': data.get('description', ''),
        'status': data.get('status', 'pending'),
        'user_id': data.get('user_id'),
        'created_at': datetime.utcnow().isoformat()
    }
    
    tasks[task_id] = task
    return jsonify(task), 201


@app.route('/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks, optionally filtered by status"""
    status = request.args.get('status')
    
    if status:
        filtered_tasks = [t for t in tasks.values() if t['status'] == status]
        return jsonify(filtered_tasks), 200
    
    return jsonify(list(tasks.values())), 200


@app.route('/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    """Get a specific task by ID"""
    if task_id not in tasks:
        return jsonify({'error': 'Task not found'}), 404
    
    return jsonify(tasks[task_id]), 200


@app.route('/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    """Update a task"""
    if task_id not in tasks:
        return jsonify({'error': 'Task not found'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    if 'title' in data:
        tasks[task_id]['title'] = data['title']
    if 'description' in data:
        tasks[task_id]['description'] = data['description']
    if 'status' in data:
        tasks[task_id]['status'] = data['status']
    if 'user_id' in data:
        tasks[task_id]['user_id'] = data['user_id']
    
    tasks[task_id]['updated_at'] = datetime.utcnow().isoformat()
    
    return jsonify(tasks[task_id]), 200


@app.route('/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    if task_id not in tasks:
        return jsonify({'error': 'Task not found'}), 404
    
    deleted_task = tasks.pop(task_id)
    return jsonify({'message': 'Task deleted', 'task': deleted_task}), 200


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Method not allowed'}), 405


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)