import os
import json
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, BadData, SignatureExpired

# Simple file-backed user store (data/users.json)
def _users_file_path():
    root = os.path.dirname(os.path.dirname(__file__))
    data_dir = os.path.join(root, 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return os.path.join(data_dir, 'users.json')


def _load_users():
    path = _users_file_path()
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def _save_users(users):
    path = _users_file_path()
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


def _get_secret():
    return os.environ.get('SECRET_KEY', 'dev_secret_key')


def register_user(username: str, password: str):
    if not username or not password:
        raise ValueError('nome e senha são obrigatórios')
    users = _load_users()
    if username in users:
        raise ValueError('usuario já existe')
    users[username] = {
        'password': generate_password_hash(password)
    }
    _save_users(users)
    return True


def authenticate_user(username: str, password: str, expires_sec: int = 3600):
    users = _load_users()
    user = users.get(username)
    if not user:
        return None
    if not check_password_hash(user['password'], password):
        return None
    s = URLSafeTimedSerializer(_get_secret(), salt='auth')
    token = s.dumps({'username': username})
    return token


def verify_token(token: str, max_age: int = 3600):
    s = URLSafeTimedSerializer(_get_secret(), salt='auth')
    try:
        data = s.loads(token, max_age=max_age)
    except SignatureExpired:
        # valid token, but expired
        return None
    except BadData:
        # invalid token
        return None
    # data could be the dict we serialized
    if isinstance(data, dict):
        return data.get('username')
    return None
