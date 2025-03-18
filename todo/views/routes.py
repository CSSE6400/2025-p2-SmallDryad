from flask import Blueprint, jsonify, request
from todo.models import db
from todo.models.todo import Todo
from datetime import datetime
 
api = Blueprint('api', __name__, url_prefix='/api/v1') 

TEST_ITEM = {
    "id": 1,
    "title": "Watch CSSE6400 Lecture",
    "description": "Watch the CSSE6400 lecture on ECHO360 for week 1",
    "completed": True,
    "deadline_at": "2023-02-27T00:00:00",
    "created_at": "2023-02-20T00:00:00",
    "updated_at": "2023-02-20T00:00:00"
}
 
@api.route('/health') 
def health():
    """Return a status of 'ok' if the server is running and listening to request"""
    return jsonify({"status": "ok"})


@api.route('/todos', methods=['GET'])
def get_todos():
    # Basic query
    todos_query = Todo.query
    # Deal with test_get_items_completed(get) fail
    # Get the data from query parameter
    completed = request.args.get('completed')
    # Check if completed parameter exist
    if completed is not None:
        # Ensure words like True TRUE turn to true check if it equal with true. So completed_bool is a boolvalue true of false
        completed_bool = completed.lower() == 'true'
        # Use filter to add a 'where' and only select the completed value equal with completed_bool
        todos_query = todos_query.filter(Todo.completed == completed_bool)    
    # Deal with test_get_items_window fail
    # Get the data from query parameter
    window = request.args.get('window')
    # Check if window parameter exist
    if window is not None:
        # Now the date now
        now = datetime.now()
        # replace the data to 0.0.0, the start of the day
        future_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        # and now and window date
        future_date = datetime(future_date.year, future_date.month, future_date.day + int(window))
        
        # select the dealine_at equal with None or <= future_date
        todos_query = todos_query.filter((Todo.deadline_at == None) | (Todo.deadline_at <= future_date))
     

    todos = todos_query.all()
    result = []
    for todo in todos:
        result.append(todo.to_dict())
    return jsonify(result)

@api.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
       return jsonify({'error': 'Todo not found'}), 404
    return jsonify(todo.to_dict())

@api.route('/todos', methods=['POST'])
def create_todo():
    # check if there have other parameters
    allowed_fields = ['title', 'description', 'completed', 'deadline_at']
    for field in request.json:
        if field not in allowed_fields:
            return jsonify({'error': f'Field {field} is not allowed'}), 400
    
    # Check the necessary parameter
    if 'title' not in request.json or not request.json['title']:
        return jsonify({'error': 'Title is required'}), 400
    
    todo = Todo(
        title=request.json.get('title'),
        description=request.json.get('description'),
        completed=request.json.get('completed', False),
    )
    
    if 'deadline_at' in request.json and request.json['deadline_at'] is not None:
        todo.deadline_at = datetime.fromisoformat(request.json.get('deadline_at'))
    
    db.session.add(todo)
    db.session.commit()
    return jsonify(todo.to_dict()), 201

@api.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    # check if there have other parameters
    allowed_fields = ['title', 'description', 'completed', 'deadline_at']
    for field in request.json:
        if field not in allowed_fields:
            return jsonify({'error': f'Field {field} is not allowed'}), 400
    
    # check if modify the id
    if 'id' in request.json:
        return jsonify({'error': 'Cannot change id'}), 400
    
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    
    todo.title = request.json.get('title', todo.title)
    todo.description = request.json.get('description', todo.description)
    todo.completed = request.json.get('completed', todo.completed)
    if 'deadline_at' in request.json:
        if request.json['deadline_at'] is not None:
            todo.deadline_at = datetime.fromisoformat(request.json.get('deadline_at'))
        else:
            todo.deadline_at = None
    
    db.session.commit()
    return jsonify(todo.to_dict())

@api.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({}), 200
    db.session.delete(todo)
    db.session.commit()
    return jsonify(todo.to_dict()), 200
