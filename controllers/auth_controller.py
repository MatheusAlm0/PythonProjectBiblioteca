from flask import Blueprint, request, jsonify
from services.auth_service import register_user, authenticate_user, verify_token

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    if not username or not password or not email:
        return jsonify({'error': 'username, email e password são obrigatórios'}), 400
    try:
        register_user(username, password, email)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    return jsonify({'message': 'usuário registrado'}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username_or_email = data.get('username') or data.get('email') or data.get('login')
    password = data.get('password')
    if not username_or_email or not password:
        return jsonify({'error': 'username/email e password são obrigatórios'}), 400
    token = authenticate_user(username_or_email, password)
    if not token:
        return jsonify({'error': 'credenciais inválidas'}), 401
    return jsonify({'token': token}), 200


@auth_bp.route('/me', methods=['GET'])
def me():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({'error': 'missing or invalid authorization header'}), 401
    token = auth_header.split(' ', 1)[1].strip()
    username = verify_token(token)
    if not username:
        return jsonify({'error': 'invalid or expired token'}), 401
    return jsonify({'username': username}), 200
