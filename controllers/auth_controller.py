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
        return jsonify({'message': 'username, email e password são obrigatórios'}), 400
    try:
        register_user(username, password, email)
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    return jsonify({'message': 'usuário cadastrado'}), 200


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username_or_email = data.get('username') or data.get('email') or data.get('login')
    password = data.get('password')
    if not username_or_email or not password:
        return jsonify({'message': 'username/email e password são obrigatórios'}), 400
    token = authenticate_user(username_or_email, password)
    if not token:
        return jsonify({'message': 'credenciais inválidas'}), 401
    return jsonify({'message': 'usuário logado'}), 200


@auth_bp.route('/me', methods=['GET'])
def me():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({'message': 'missing or invalid authorization header'}), 401
    token = auth_header.split(' ', 1)[1].strip()
    username = verify_token(token)
    if not username:
        return jsonify({'message': 'invalid or expired token'}), 401
    return jsonify({'message': username}), 200
