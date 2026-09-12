from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, SocialShare, Habit
from datetime import datetime
import urllib.parse

social_bp = Blueprint('social', __name__, url_prefix='/api/social')

def generate_share_message(habit, platform, stats=None):
    """Generate platform-specific share messages"""
    if not stats:
        stats = {'completion_rate': 0, 'total_completions': 0}
    
    messages = {
        'twitter': f"I just completed {habit.name}! 🎯 Keep up the habit streak on #HabitTrack {' 📊 ' + str(stats.get('completion_rate', 0)) + '% completion rate' if stats else ''}",
        'facebook': f"🎯 Tracking my progress on '{habit.name}' using #HabitTrack! Currently at {stats.get('completion_rate', 0)}% completion rate with {stats.get('total_completions', 0)} completions. Building better habits! 💪",
        'linkedin': f"I'm building better habits with #HabitTrack! Currently tracking '{habit.name}' with a {stats.get('completion_rate', 0)}% completion rate. Consistency is key to personal development! 📈",
        'reddit': f"Just tracked '{habit.name}' using HabitTrack! {stats.get('total_completions', 0)} completions and {stats.get('completion_rate', 0)}% completion rate so far. Great app for habit tracking! 🎯",
        'whatsapp': f"Check out my habit tracking progress on {habit.name}! {stats.get('completion_rate', 0)}% completion rate 📊 #HabitTrack",
        'telegram': f"📊 Habit Update: {habit.name}\nCompletion Rate: {stats.get('completion_rate', 0)}%\nTotal Completions: {stats.get('total_completions', 0)}\nTracking with #HabitTrack"
    }
    
    return messages.get(platform, f"I'm tracking '{habit.name}' on #HabitTrack")

def get_share_url(habit, platform, message):
    """Generate share URLs for different platforms"""
    base_url = 'http://localhost:3000'  # Frontend URL
    share_link = f"{base_url}/share/{habit.id}"
    
    urls = {
        'twitter': f"https://twitter.com/intent/tweet?text={urllib.parse.quote(message)}&url={urllib.parse.quote(share_link)}",
        'facebook': f"https://www.facebook.com/sharer/sharer.php?u={urllib.parse.quote(share_link)}",
        'linkedin': f"https://www.linkedin.com/sharing/share-offsite/?url={urllib.parse.quote(share_link)}",
        'reddit': f"https://reddit.com/submit?url={urllib.parse.quote(share_link)}&title={urllib.parse.quote(habit.name)}",
        'whatsapp': f"https://wa.me/?text={urllib.parse.quote(message + ' ' + share_link)}",
        'telegram': f"https://t.me/share/url?url={urllib.parse.quote(share_link)}&text={urllib.parse.quote(message)}",
    }
    
    return urls.get(platform, share_link)

@social_bp.route('/share/<habit_id>/<platform>', methods=['POST'])
@login_required
def share_habit(habit_id, platform):
    """Create and track a social share"""
    try:
        habit = Habit.query.filter_by(
            id=habit_id,
            user_id=current_user.id
        ).first()
        
        if not habit:
            return jsonify({'error': 'Habit not found'}), 404
        
        # Validate platform
        valid_platforms = ['twitter', 'facebook', 'linkedin', 'reddit', 'whatsapp', 'telegram']
        if platform not in valid_platforms:
            return jsonify({'error': f'Invalid platform. Must be one of: {", ".join(valid_platforms)}'}), 400
        
        # Get habit stats
        from models import HabitCompletion
        completions = HabitCompletion.query.filter_by(
            habit_id=habit_id,
            completed=True
        ).count()
        
        total_days = (datetime.utcnow().date() - habit.created_at.date()).days + 1
        completion_rate = round((completions / total_days * 100)) if total_days > 0 else 0
        
        stats = {
            'completion_rate': completion_rate,
            'total_completions': completions
        }
        
        # Generate message and URL
        message = generate_share_message(habit, platform, stats)
        share_url = get_share_url(habit, platform, message)
        
        # Record share in database
        social_share = SocialShare(
            user_id=current_user.id,
            habit_id=habit_id,
            platform=platform,
            message=message,
            share_url=share_url
        )
        
        db.session.add(social_share)
        db.session.commit()
        
        return jsonify({
            'message': 'Share prepared successfully',
            'share_url': share_url,
            'share_message': message,
            'platform': platform
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@social_bp.route('/share/stats', methods=['GET'])
@login_required
def get_share_stats():
    """Get social sharing statistics for current user"""
    try:
        shares = SocialShare.query.filter_by(user_id=current_user.id).all()
        
        stats = {
            'total_shares': len(shares),
            'by_platform': {}
        }
        
        for share in shares:
            platform = share.platform
            stats['by_platform'][platform] = stats['by_platform'].get(platform, 0) + 1
        
        return jsonify(stats), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@social_bp.route('/platforms', methods=['GET'])
def get_platforms():
    """Get available sharing platforms"""
    platforms = [
        {
            'id': 'twitter',
            'name': 'Twitter/X',
            'icon': '𝕏',
            'color': '#000000'
        },
        {
            'id': 'facebook',
            'name': 'Facebook',
            'icon': 'f',
            'color': '#1877F2'
        },
        {
            'id': 'linkedin',
            'name': 'LinkedIn',
            'icon': 'in',
            'color': '#0A66C2'
        },
        {
            'id': 'reddit',
            'name': 'Reddit',
            'icon': 'r',
            'color': '#FF4500'
        },
        {
            'id': 'whatsapp',
            'name': 'WhatsApp',
            'icon': 'W',
            'color': '#25D366'
        },
        {
            'id': 'telegram',
            'name': 'Telegram',
            'icon': 'T',
            'color': '#0088cc'
        }
    ]
    
    return jsonify(platforms), 200
