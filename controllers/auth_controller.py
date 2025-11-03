from flask import Blueprint, request, jsonify
from data.db import SessionLocal, User
from services.session_manager import login_user, logout_user, get_logged_users, is_logged_in

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not username or not password or not email:
        return jsonify({'error': 'Nome, email e senha são obrigatórios'}), 400

    session = SessionLocal()
    try:
        existing = session.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing:
            if existing.username == username:
                return jsonify({'error': 'Usuário já cadastrado'}), 400
            else:
                return jsonify({'error': 'email já cadastrado'}), 400

        new_user = User(username=username, email=email, password=password)
        session.add(new_user)
        session.commit()

        return jsonify({
            'message': 'Usuário cadastrado com sucesso',
            'user_id': str(new_user.id),
            'username': new_user.username
        }), 201

    except Exception as e:
        session.rollback()
        return jsonify({'error': f'Erro ao cadastrar: {str(e)}'}), 500
    finally:
        session.close()


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username_or_email = data.get('username') or data.get('email') or data.get('login')
    password = data.get('password')

    if not username_or_email or not password:
        return jsonify({'error': 'Email e senha são obrigatórios'}), 400

    session = SessionLocal()
    try:
        user = session.query(User).filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()

        if not user or user.password != password:
            return jsonify({'error': 'Email ou senha incorretos'}), 401

        user_id = str(user.id)

        login_user(user_id)

        return jsonify({
            'message': 'Login realizado com sucesso',
            'user_id': user_id,
            'username': user.username,
            'email': user.email
        }), 200

    finally:
        session.close()


@auth_bp.route('/logout', methods=['POST'])
def logout():
    data = request.get_json() or {}
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({'error': 'Parece que houve um erro ao tentar fazer logout.'}), 400

    logout_user(user_id)

    return jsonify({'message': 'Logout realizado com sucesso'}), 200


@auth_bp.route('/me', methods=['GET'])
def me():
    auth_header = request.headers.get('Authorization', '')
    user_id = None

    if auth_header.startswith('Bearer '):
        user_id = auth_header.split(' ', 1)[1].strip()
    elif auth_header:
        user_id = auth_header
    else:
        user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({'error': 'Sessão não encontrada. Faça login novamente.'}), 401

    if not is_logged_in(user_id):
        return jsonify({'error': 'Sessão expirada. Faça login novamente.'}), 401

    session = SessionLocal()
    try:
        user = session.query(User).filter(User.id == user_id).first()

        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404

        return jsonify({
            'username': user.username,
            'email': user.email,
            'user_id': str(user.id)
        }), 200

    finally:
        session.close()


@auth_bp.route('/status', methods=['GET'])
def status():
    return jsonify({
        'logged_users': get_logged_users(),
        'total': len(get_logged_users())
    }), 200