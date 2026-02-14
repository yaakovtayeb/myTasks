from flask import Flask, render_template, request, jsonify
from datetime import datetime
from werkzeug.middleware.proxy_fix import ProxyFix
from config import Config
from storage import StorageManager
from task_manager import TaskManager
from models import Task

app = Flask(__name__)
app.config.from_object(Config)

# Enable ProxyFix to work behind reverse proxies (like SageMaker)
# This allows the app to work both locally and behind proxies
app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,
    x_proto=1,
    x_host=1,
    x_prefix=1
)

# Initialize storage and task manager
storage = StorageManager()
task_manager = TaskManager(storage)


# View Routes
@app.route('/')
def index():
    """Main task list view."""
    tasks = task_manager.get_all_tasks_ordered()
    config = storage.load_config()
    return render_template('index.html', tasks=tasks, config=config)


@app.route('/settings')
def settings():
    """Settings page."""
    config = storage.load_config()
    return render_template('settings.html', config=config)


@app.route('/print')
def print_view():
    """Print view for tasks."""
    include_backlog = request.args.get('backlog', 'false').lower() == 'true'
    tasks = task_manager.get_all_tasks_ordered()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    return render_template('print.html', tasks=tasks, include_backlog=include_backlog, now=now)


# API Routes - Tasks
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks grouped by status."""
    tasks = task_manager.get_all_tasks_ordered()
    return jsonify({
        'historical': [t.to_dict() for t in tasks['historical']],
        'current': [t.to_dict() for t in tasks['current']],
        'backlog': [t.to_dict() for t in tasks['backlog']]
    })


@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Create a new task."""
    data = request.json

    title = data.get('title', '').strip()
    if not title:
        return jsonify({'success': False, 'message': 'Title is required'}), 400

    task_type = data.get('type', 'customer engagement')
    status = data.get('status', 'backlog')
    time_estimate = data.get('time_estimate', '')
    notes = data.get('notes', '')
    links = data.get('links', [])

    success, message, task = task_manager.add_task(
        title=title,
        task_type=task_type,
        status=status,
        time_estimate=time_estimate,
        notes=notes,
        links=links
    )

    if success:
        return jsonify({
            'success': True,
            'message': message,
            'task': task.to_dict()
        })
    else:
        return jsonify({'success': False, 'message': message}), 400


@app.route('/api/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    """Get a specific task."""
    task = task_manager.get_task(task_id)
    if task:
        return jsonify({'success': True, 'task': task.to_dict()})
    else:
        return jsonify({'success': False, 'message': 'Task not found'}), 404


@app.route('/api/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    """Update a task."""
    data = request.json
    success, message = task_manager.update_task(task_id, **data)

    if success:
        task = task_manager.get_task(task_id)
        return jsonify({
            'success': True,
            'message': message,
            'task': task.to_dict()
        })
    else:
        return jsonify({'success': False, 'message': message}), 400


@app.route('/api/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task."""
    success, message = task_manager.delete_task(task_id)

    if success:
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'success': False, 'message': message}), 404


@app.route('/api/tasks/<task_id>/complete', methods=['POST'])
def complete_task(task_id):
    """Mark a task as completed."""
    data = request.json
    finish_date = data.get('finish_date', '')

    if not finish_date:
        return jsonify({'success': False, 'message': 'Finish date is required'}), 400

    success, message = task_manager.complete_task(task_id, finish_date)

    if success:
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'success': False, 'message': message}), 400


@app.route('/api/tasks/<task_id>/current', methods=['POST'])
def move_to_current(task_id):
    """Move a task from backlog to current."""
    success, message = task_manager.move_to_current(task_id)

    if success:
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'success': False, 'message': message}), 400


@app.route('/api/tasks/<task_id>/subtasks', methods=['POST'])
def add_subtask(task_id):
    """Add a subtask to a task."""
    data = request.json
    subtask_title = data.get('title', '').strip()

    if not subtask_title:
        return jsonify({'success': False, 'message': 'Subtask title is required'}), 400

    success, message = task_manager.add_subtask(task_id, subtask_title)

    if success:
        task = task_manager.get_task(task_id)
        return jsonify({
            'success': True,
            'message': message,
            'task': task.to_dict()
        })
    else:
        return jsonify({'success': False, 'message': message}), 400


@app.route('/api/tasks/<task_id>/subtasks/<subtask_id>/toggle', methods=['POST'])
def toggle_subtask(task_id, subtask_id):
    """Toggle subtask completion."""
    success, message = task_manager.toggle_subtask(task_id, subtask_id)

    if success:
        task = task_manager.get_task(task_id)
        return jsonify({
            'success': True,
            'message': message,
            'task': task.to_dict()
        })
    else:
        return jsonify({'success': False, 'message': message}), 400


# API Routes - Config
@app.route('/api/config', methods=['GET'])
def get_config():
    """Get application configuration."""
    config = storage.load_config()
    return jsonify(config.to_dict())


@app.route('/api/config', methods=['PUT'])
def update_config():
    """Update application configuration."""
    data = request.json
    config = storage.load_config()

    if 'task_types' in data:
        config.task_types = data['task_types']
    if 'max_active_tasks' in data:
        config.max_active_tasks = data['max_active_tasks']
    if 'auto_scroll_to_current' in data:
        config.auto_scroll_to_current = data['auto_scroll_to_current']

    storage.save_config(config)
    return jsonify({'success': True, 'message': 'Configuration updated', 'config': config.to_dict()})


if __name__ == '__main__':
    app.run(host=app.config['HOST'], port=app.config['PORT'], debug=app.config['DEBUG'])
