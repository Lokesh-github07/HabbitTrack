from datetime import date, datetime

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from models import Task, db

tasks_bp = Blueprint('tasks', __name__, url_prefix='/api/tasks')


def owned_task(task_id):
    return Task.query.filter_by(id=task_id, user_id=current_user.id).first()


@tasks_bp.route('', methods=['GET'])
@login_required
def list_tasks():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    tasks.sort(key=lambda task: (task.completed, task.due_date or date.max, task.id or ''))
    return jsonify([task.to_dict() for task in tasks])


@tasks_bp.route('', methods=['POST'])
@login_required
def create_task():
    data = request.get_json() or {}
    title = (data.get('title') or '').strip()
    if not title:
        return jsonify({'error': 'Task title is required'}), 400
    try:
        due_date = datetime.fromisoformat(data['due_date']).date() if data.get('due_date') else None
    except ValueError:
        return jsonify({'error': 'Due date must use YYYY-MM-DD'}), 400
    task = Task(user_id=current_user.id, title=title, due_date=due_date)
    db.session.add(task)
    db.session.commit()
    return jsonify({'message': 'Task created', 'task': task.to_dict()}), 201


@tasks_bp.route('/<task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    task = owned_task(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    data = request.get_json() or {}
    if 'title' in data:
        title = (data['title'] or '').strip()
        if not title:
            return jsonify({'error': 'Task title is required'}), 400
        task.title = title
    if 'completed' in data:
        task.completed = bool(data['completed'])
    if 'due_date' in data:
        try:
            task.due_date = datetime.fromisoformat(data['due_date']).date() if data['due_date'] else None
        except ValueError:
            return jsonify({'error': 'Due date must use YYYY-MM-DD'}), 400
    db.session.add(task)
    db.session.commit()
    return jsonify({'message': 'Task updated', 'task': task.to_dict()})


@tasks_bp.route('/<task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    task = owned_task(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted'})
