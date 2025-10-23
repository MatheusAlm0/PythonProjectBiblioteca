import os
from flask import Flask, render_template
from flask_cors import CORS
from controllers.book_controller import book_bp
from controllers.chat_controller import chat_bp
from controllers.auth_controller import auth_bp

# Remove token HF do ambiente para testar API pública
if 'HUGGINGFACE_API_KEY' in os.environ:
    print("[DEBUG] Removendo HUGGINGFACE_API_KEY do ambiente")
    del os.environ['HUGGINGFACE_API_KEY']

app = Flask(__name__)
CORS(app)
app.register_blueprint(book_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(auth_bp)


@app.route('/')
def index():
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == "__main__":
    app.run(debug=True, port=5000)