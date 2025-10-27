import sys
import os

# CRÍTICO: Forçar encoding UTF-8 no Windows ANTES de qualquer outro import
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PGCLIENTENCODING'] = 'UTF8'

from flask import Flask, render_template
from flask_cors import CORS
from controllers.book_controller import book_bp
from controllers.chat_controller import chat_bp
from controllers.auth_controller import auth_bp
from controllers.rating_controller import rating_bp
from data.db import init_db

app = Flask(__name__)
CORS(app)

# Remove token HF do ambiente para testar API pública
if 'HUGGINGFACE_API_KEY' in os.environ:
    print("[DEBUG] Removendo HUGGINGFACE_API_KEY do ambiente")
    del os.environ['HUGGINGFACE_API_KEY']

init_db()  # Inicializa o banco de dados
app.register_blueprint(book_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(rating_bp)


@app.route('/')
def index():
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == "__main__":
    app.run(debug=True, port=5000)