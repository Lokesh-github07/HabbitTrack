from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, Habit, HabitCompletion
from datetime import datetime, date

habits_bp = Blueprint('habits', __name__, url_prefix='/api/habits')


def serialize_habit(habit):
    data = habit.to_dict()
    completions = HabitCompletion.query.filter_by(habit_id=habit.id).all()
    data['completions'] = [completion.to_dict() for completion in completions]
    return data

@habits_bp.route('', methods=['GET'])
@login_required
def get_habits():
    """Get all habits for current user"""
    try:
        habits = Habit.query.filter_by(user_id=current_user.id).all()
        return jsonify([serialize_habit(habit) for habit in habits]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@habits_bp.route('', methods=['POST'])
@login_required
def create_habit():
    """Create a new habit"""
    try:
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({'error': 'Habit name required'}), 400
        
        habit = Habit(
            user_id=current_user.id,
            name=data['name'],
            description=data.get('description', '')
        )
        
        db.session.add(habit)
        db.session.commit()
        
        return jsonify({
            'message': 'Habit created',
            'habit': serialize_habit(habit)
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@habits_bp.route('/<int:habit_id>', methods=['GET'])
@login_required
def get_habit(habit_id):
    """Get a specific habit"""
    try:
        habit = Habit.query.filter_by(
            id=habit_id,
            user_id=current_user.id
        ).first()
        
        if not habit:
            return jsonify({'error': 'Habit not found'}), 404
        
        return jsonify(serialize_habit(habit)), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@habits_bp.route('/<int:habit_id>', methods=['PUT'])
@login_required
def update_habit(habit_id):
    """Update a habit"""
    try:
        habit = Habit.query.filter_by(
            id=habit_id,
            user_id=current_user.id
        ).first()
        
        if not habit:
            return jsonify({'error': 'Habit not found'}), 404
        
        data = request.get_json()
        
        if 'name' in data:
            habit.name = data['name']
        if 'description' in data:
            habit.description = data['description']
        
        habit.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Habit updated',
            'habit': serialize_habit(habit)
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@habits_bp.route('/<int:habit_id>', methods=['DELETE'])
@login_required
def delete_habit(habit_id):
    """Delete a habit"""
    try:
        habit = Habit.query.filter_by(
            id=habit_id,
            user_id=current_user.id
        ).first()
        
        if not habit:
            return jsonify({'error': 'Habit not found'}), 404
        
        db.session.delete(habit)
        db.session.commit()
        
        return jsonify({'message': 'Habit deleted'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@habits_bp.route('/<int:habit_id>/toggle', methods=['POST'])
@login_required
def toggle_completion(habit_id):
    """Toggle habit completion for a date"""
    try:
        habit = Habit.query.filter_by(
            id=habit_id,
            user_id=current_user.id
        ).first()
        
        if not habit:
            return jsonify({'error': 'Habit not found'}), 404
        
        data = request.get_json()
        completion_date = datetime.fromisoformat(data.get('date', str(date.today()))).date()
        
        completion = HabitCompletion.query.filter_by(
            habit_id=habit_id,
            date=completion_date
        ).first()
        
        if completion:
            completion.completed = not completion.completed
        else:
            completion = HabitCompletion(
                habit_id=habit_id,
                date=completion_date,
                completed=True
            )
            db.session.add(completion)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Completion toggled',
            'completion': completion.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@habits_bp.route('/<int:habit_id>/stats', methods=['GET'])
@login_required
def get_habit_stats(habit_id):
    """Get statistics for a habit"""
    try:
        habit = Habit.query.filter_by(
            id=habit_id,
            user_id=current_user.id
        ).first()
        
        if not habit:
            return jsonify({'error': 'Habit not found'}), 404
        
        completions = HabitCompletion.query.filter_by(
            habit_id=habit_id,
            completed=True
        ).all()
        
        total_days = (datetime.utcnow().date() - habit.created_at.date()).days + 1
        completion_rate = round((len(completions) / total_days * 100)) if total_days > 0 else 0
        
        return jsonify({
            'habit_id': habit_id,
            'total_completions': len(completions),
            'completion_rate': completion_rate,
            'days_tracked': total_days
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
