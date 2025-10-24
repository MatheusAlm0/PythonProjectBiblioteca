import sys
import os
import locale

print("=" * 60)
print("DIAGNÓSTICO DO PROBLEMA DE ENCODING")
print("=" * 60)

# 1. Encoding do sistema
print("\n1. ENCODING DO SISTEMA:")
print(f"   sys.getdefaultencoding(): {sys.getdefaultencoding()}")
print(f"   sys.getfilesystemencoding(): {sys.getfilesystemencoding()}")
print(f"   locale.getpreferredencoding(): {locale.getpreferredencoding()}")

# 2. Variáveis de ambiente relevantes
print("\n2. VARIÁVEIS DE AMBIENTE:")
env_vars = ['PGCLIENTENCODING', 'PYTHONIOENCODING', 'LC_ALL', 'LANG', 'PGPASSFILE', 'PGSERVICEFILE']
for var in env_vars:
    value = os.environ.get(var, 'NÃO DEFINIDA')
    print(f"   {var}: {value}")

# 3. Caminhos importantes
print("\n3. CAMINHOS DO SISTEMA:")
print(f"   HOME: {os.environ.get('HOME', 'NÃO DEFINIDA')}")
print(f"   USERPROFILE: {os.environ.get('USERPROFILE', 'NÃO DEFINIDA')}")
print(f"   APPDATA: {os.environ.get('APPDATA', 'NÃO DEFINIDA')}")

# 4. Verificar se existe .pgpass
print("\n4. ARQUIVOS DE CONFIGURAÇÃO POSTGRESQL:")
possible_pgpass = [
    os.path.join(os.environ.get('APPDATA', ''), 'postgresql', 'pgpass.conf'),
    os.path.join(os.environ.get('USERPROFILE', ''), '.pgpass'),
    os.path.join(os.environ.get('HOME', ''), '.pgpass'),
]

for path in possible_pgpass:
    if os.path.exists(path):
        print(f"   ✓ ENCONTRADO: {path}")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"      → Legível em UTF-8")
        except UnicodeDecodeError as e:
            print(f"      ✗ ERRO DE ENCODING AQUI! {e}")
    else:
        print(f"   ✗ Não existe: {path}")

# 5. Tentar conexão direta com psycopg2
print("\n5. TESTE DE CONEXÃO PSYCOPG2:")
try:
    import psycopg2

    print("   Tentando conectar...")

    # Teste 1: Sem encoding especificado
    try:
        conn = psycopg2.connect(
            host='127.0.0.1',
            port=5432,
            user='postgres',
            password='postgres',
            database='biblioteca'
        )
        print("   ✓ Conexão SEM client_encoding: OK")
        conn.close()
    except Exception as e:
        print(f"   ✗ Conexão SEM client_encoding: FALHOU")
        print(f"      Erro: {str(e)[:100]}")

    # Teste 2: Com encoding UTF8
    try:
        conn = psycopg2.connect(
            host='127.0.0.1',
            port=5432,
            user='postgres',
            password='postgres',
            database='biblioteca',
            client_encoding='UTF8'
        )
        print("   ✓ Conexão COM client_encoding='UTF8': OK")
        conn.close()
    except Exception as e:
        print(f"   ✗ Conexão COM client_encoding='UTF8': FALHOU")
        print(f"      Erro: {str(e)[:100]}")

except ImportError:
    print("   ✗ psycopg2 não instalado")

print("\n" + "=" * 60)
print("FIM DO DIAGNÓSTICO")
print("=" * 60)