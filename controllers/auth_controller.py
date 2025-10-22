from flask import Blueprint, request, jsonify
from services.auth_service import register_user, authenticate_user, verify_token

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'username and password required'}), 400
    try:
        register_user(username, password)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    return jsonify({'message': 'user registered'}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'username and password required'}), 400
    token = authenticate_user(username, password)
    if not token:
        return jsonify({'error': 'invalid credentials'}), 401
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

