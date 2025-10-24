from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP, text
from sqlalchemy.orm import declarative_base, sessionmaker
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'biblioteca.db')
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={'check_same_thread': False}
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(150), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))

def init_db():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        if not session.query(User).filter_by(username='teste').first():
            session.add(User(username='teste', password='senha123'))
        if not session.query(User).filter_by(username='meuUsuario').first():
            session.add(User(username='meuUsuario', password='senha123'))
        session.commit()
    finally:
        session.close()

if __name__ == '__main__':
    try:
        with engine.connect() as conn:
            print("Conexão com SQLite OK!")
        init_db()
        print("Banco inicializado com sucesso!")
    except Exception as e:
        print(f"Erro: {e}")