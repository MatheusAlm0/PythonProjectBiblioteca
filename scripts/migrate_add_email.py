import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'biblioteca.db')

print('Usando DB em:', DB_PATH)
if not os.path.exists(DB_PATH):
    print('Arquivo de banco não encontrado:', DB_PATH)
    raise SystemExit(1)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Verifica se a coluna 'email' já existe
cur.execute("PRAGMA table_info(users);")
cols = [r[1] for r in cur.fetchall()]
print('Colunas atuais:', cols)
if 'email' in cols:
    print('Coluna email já existe. Nada a fazer.')
    conn.close()
    raise SystemExit(0)

try:
    print('Adicionando coluna email...')
    cur.execute("ALTER TABLE users ADD COLUMN email VARCHAR(255);")
    conn.commit()
    print('Coluna adicionada. Atualizando registros existentes...')
    # popular emails com username@local se estiverem nulos
    cur.execute("SELECT id, username FROM users;")
    rows = cur.fetchall()
    for r in rows:
        uid, username = r
        email = f"{username}@local"
        cur.execute("UPDATE users SET email = ? WHERE id = ?", (email, uid))
    conn.commit()
    print('Registros atualizados.')
except Exception as e:
    print('Erro durante migração:', e)
    conn.rollback()
    raise
finally:
    conn.close()

print('Migração concluída com sucesso.')

