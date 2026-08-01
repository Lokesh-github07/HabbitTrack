import os
from flask import Flask, jsonify, send_from_directory
from flask_login import LoginManager
from flask_cors import CORS
from dotenv import load_dotenv

from config import config_by_name
from models import db, User
from routes.auth import auth_bp
from routes.habits import habits_bp
from routes.social import social_bp

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))


def create_app(config_name='development'):
    """Application factory"""
    app = Flask(__name__)
    app.config['JSON_SORT_KEYS'] = False

    config_class = config_by_name.get(config_name, config_by_name['development'])
    app.config.from_object(config_class)

    db.init_app(app)
    CORS(app, supports_credentials=True)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(int(user_id))

    app.register_blueprint(auth_bp)
    app.register_blueprint(habits_bp)
    app.register_blueprint(social_bp)

    with app.app_context():
        db.create_all()

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    @app.route('/')
    def index():
        return send_from_directory(project_root, 'index.html')

    @app.route('/index.html')
    def index_file():
        return send_from_directory(project_root, 'index.html')

    @app.route('/styles.css')
    def styles():
        return send_from_directory(project_root, 'styles.css')

    @app.route('/app.js')
    def app_js():
        return send_from_directory(project_root, 'app.js')

    @app.route('/frontend/<path:path>')
    def frontend_files(path):
        return send_from_directory(os.path.join(project_root, 'frontend'), path)

    @app.route('/api/health', methods=['GET'])
    def health():
        return jsonify({'status': 'healthy', 'message': 'HabitTrack API is running'}), 200

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Resource not found'}), 404

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

    return app


if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('FLASK_DEBUG', True),
    )
