import os
from itsdangerous import URLSafeTimedSerializer, BadData, SignatureExpired
from data.db import SessionLocal, User


def _get_secret():
    return os.environ.get('SECRET_KEY', 'dev_secret_key')


def register_user(username: str, password: str):
    if not username or not password:
        raise ValueError('nome e senha são obrigatórios')
    session = SessionLocal()
    try:
        existing = session.query(User).filter_by(username=username).first()
        if existing:
            raise ValueError('usuario já existe')
        new_user = User(username=username, password=password)  # senha em texto simples
        session.add(new_user)
        session.commit()
        return True
    finally:
        session.close()


def authenticate_user(username: str, password: str, expires_sec: int = 3600):
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(username=username).first()
        if not user or user.password != password:  # comparação direta, sem hash
            return None
        s = URLSafeTimedSerializer(_get_secret(), salt='auth')
        token = s.dumps({'username': username})
        return token
    finally:
        session.close()


def verify_token(token: str, max_age: int = 3600):
    s = URLSafeTimedSerializer(_get_secret(), salt='auth')
    try:
        data = s.loads(token, max_age=max_age)
    except SignatureExpired:
        return None
    except BadData:
        return None
    if isinstance(data, dict):
        return data.get('username')
    return None
