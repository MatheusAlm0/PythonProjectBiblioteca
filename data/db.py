from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP, Text, ForeignKey, UniqueConstraint, CheckConstraint, text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
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
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    
    # Relacionamento com avaliações
    avaliacoes = relationship('Avaliacao', back_populates='usuario')


class Livro(Base):
    __tablename__ = 'livros'
    
    id = Column(Integer, primary_key=True)
    google_books_id = Column(String(50), unique=True, nullable=False, index=True)
    titulo = Column(String(255), nullable=False)
    subtitulo = Column(String(255))
    autores = Column(Text)
    editora = Column(String(255))
    data_publicacao = Column(String(50))
    descricao = Column(Text)
    num_paginas = Column(Integer)
    categorias = Column(Text)
    idioma = Column(String(10))
    thumbnail_url = Column(String(500))
    preview_link = Column(String(500))
    info_link = Column(String(500))
    data_adicao = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    
    # Relacionamento com avaliações
    avaliacoes = relationship('Avaliacao', back_populates='livro', cascade='all, delete-orphan')


class Avaliacao(Base):
    __tablename__ = 'avaliacoes'
    __table_args__ = (
        UniqueConstraint('livro_id', 'usuario_id', name='uq_livro_usuario'),
        CheckConstraint('estrelas >= 1 AND estrelas <= 5', name='ck_estrelas_range')
    )
    
    id = Column(Integer, primary_key=True)
    livro_id = Column(Integer, ForeignKey('livros.id'), nullable=False, index=True)
    usuario_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    estrelas = Column(Integer, nullable=False)
    comentario = Column(Text)
    data_avaliacao = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    
    # Relacionamentos
    livro = relationship('Livro', back_populates='avaliacoes')
    usuario = relationship('User', back_populates='avaliacoes')


def get_db():
    """Generator que fornece uma sessão do banco e fecha automaticamente"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session():
    """Retorna uma nova sessão do banco"""
    return SessionLocal()


def init_db():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        if not session.query(User).filter_by(username='teste').first():
            session.add(User(username='teste', email='teste@local', password='senha123'))
        if not session.query(User).filter_by(username='meuUsuario').first():
            session.add(User(username='meuUsuario', email='meuUsuario@local', password='senha123'))
        session.commit()
        print("✅ Banco de dados inicializado com sucesso!")
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