import os
import psycopg2

# Configurações do banco PostgreSQL (hardcoded)
DB_USER = 'postgres'
DB_PASS = 'postgres'  # Senha com acento, ajuste se necessário
DB_HOST = '127.0.0.1'
DB_PORT = 5432

# Caminho do arquivo SQL
SQL_FILE = os.path.join(os.path.dirname(__file__), 'data.sql')

def run_sql():
    # Conecta ao banco 'postgres' para criar o banco 'biblioteca'
    conn = psycopg2.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, port=DB_PORT, database='postgres')
    conn.autocommit = True
    cur = conn.cursor()

    try:
        cur.execute("CREATE DATABASE biblioteca;")
        print("Banco 'biblioteca' criado.")
    except psycopg2.errors.DuplicateDatabase:
        print("Banco 'biblioteca' já existe.")
    except Exception as e:
        print(f"Erro ao criar banco: {e}")

    cur.close()
    conn.close()

    # Agora conecta ao banco 'biblioteca' e executa o resto do SQL
    conn = psycopg2.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, port=DB_PORT, database='biblioteca', options="-c client_encoding=utf8")
    cur = conn.cursor()

    with open(SQL_FILE, 'r', encoding='cp1252') as f:
        sql = f.read()

    # Divide por ; e executa (ignorando CREATE DATABASE)
    statements = [s.strip() for s in sql.split(';') if s.strip() and not s.upper().startswith('CREATE DATABASE')]
    for stmt in statements:
        print(f"Executando: {stmt[:50]}...")
        cur.execute(stmt)

    conn.commit()
    cur.close()
    conn.close()
    print("Tabela criada e dados inseridos automaticamente!")

if __name__ == '__main__':
    run_sql()
