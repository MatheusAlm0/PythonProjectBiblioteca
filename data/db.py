from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP, text
from sqlalchemy.orm import declarative_base, sessionmaker
import os

# ============================================================================
# CONFIGURAÇÃO COM SQLITE - Simples, rápido e SEM problemas de encoding!
# ============================================================================

# Caminho do banco de dados SQLite
DB_PATH = os.path.join(os.path.dirname(__file__), 'biblioteca.db')
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Criar engine
engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={'check_same_thread': False}  # Necessário para Flask
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


# ============================================================================
# MODELS
# ============================================================================

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(150), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))


# ============================================================================
# FUNÇÕES
# ============================================================================

def init_db():
    """Inicializa o banco de dados e cria usuários padrão"""
    try:
        print("🔄 Iniciando criação de tabelas...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tabelas criadas com sucesso!")

        # Inserts automáticos
        session = SessionLocal()
        try:
            # Verificar e criar usuários padrão
            if not session.query(User).filter_by(username='teste').first():
                session.add(User(username='teste', password='senha123'))
                print("✅ Usuário 'teste' criado")
            else:
                print("ℹ️  Usuário 'teste' já existe")

            if not session.query(User).filter_by(username='meuUsuario').first():
                session.add(User(username='meuUsuario', password='senha123'))
                print("✅ Usuário 'meuUsuario' criado")
            else:
                print("ℹ️  Usuário 'meuUsuario' já existe")

            session.commit()
            print(f"✅ Banco SQLite inicializado: {DB_PATH}")
            print("=" * 60)
        except Exception as e:
            print(f"❌ Erro ao inserir dados: {e}")
            session.rollback()
            raise
        finally:
            session.close()
    except Exception as e:
        print(f"❌ Erro ao inicializar banco: {e}")
        import traceback
        traceback.print_exc()
        raise


# ============================================================================
# TESTE DE CONEXÃO
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("TESTE DE CONEXÃO COM SQLITE")
    print("=" * 60)

    try:
        # Testar conexão
        with engine.connect() as conn:
            print("✅ Conexão com SQLite OK!")

            # Testar query
            result = conn.execute(text("SELECT sqlite_version()"))
            version = result.scalar()
            print(f"✅ SQLite version: {version}")

        # Inicializar banco
        init_db()

        # Testar leitura de usuários
        session = SessionLocal()
        try:
            users = session.query(User).all()
            print(f"\n✅ Total de usuários no banco: {len(users)}")
            for user in users:
                print(f"   - {user.username} (ID: {user.id})")
        finally:
            session.close()

        print("\n" + "=" * 60)
        print("✅ TUDO FUNCIONANDO PERFEITAMENTE!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback

        traceback.print_exc()