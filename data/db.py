from sqlalchemy import create_engine, Column, String, TIMESTAMP, text, Text, Integer, UniqueConstraint, CheckConstraint, \
    ForeignKey, JSON
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import uuid

# Alterado para usar SQLite local em vez de PostgreSQL
DATABASE_URL = "sqlite:///./biblioteca.db"

# Para SQLite é recomendado passar connect_args para permitir uso em múltiplas threads (Flask, etc.)
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    # Armazenar UUIDs como strings para compatibilidade com SQLite
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(150), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    # Usar JSON genérico do SQLAlchemy (funciona como TEXT em SQLite)
    favorite_books = Column(JSON, default=list)
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))

    avaliacoes = relationship('Avaliacao', back_populates='usuario', cascade='all, delete-orphan')


class Avaliacao(Base):
    __tablename__ = 'avaliacoes'
    __table_args__ = (
        UniqueConstraint('google_books_id', 'usuario_id', name='uq_livro_usuario'),
        CheckConstraint('estrelas >= 1 AND estrelas <= 5', name='ck_estrelas_range')
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    google_books_id = Column(String(50), nullable=False, index=True)
    estrelas = Column(Integer, nullable=False)
    comentario = Column(Text)
    data_avaliacao = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), onupdate=text('CURRENT_TIMESTAMP'))
    usuario_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)

    usuario = relationship('User', back_populates='avaliacoes')


def init_db():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        usuarios_padrao = [
            {
                'username': 'Teste',
                'email': 'teste@local.com',
                'password': 'senha123',
                'favorite_books': [
                    'zyTCAlFPjgYC',
                    'wrOQLV6xB-wC',
                    'nggnmAEACAAJ'
                ]
            },
            {
                'username': 'Matheus',
                'email': 'matheus@gmail.com',
                'password': 'senha123',
                'favorite_books': [
                    'PXa2bby0oQ0C',
                    'IwywDwAAQBAJ',
                    '1wy49d1FmLcC'
                ]
            }
        ]

        for user_data in usuarios_padrao:
            if not session.query(User).filter_by(username=user_data['username']).first():
                session.add(User(**user_data))

        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Erro ao inicializar usuários: {e}")
    finally:
        session.close()