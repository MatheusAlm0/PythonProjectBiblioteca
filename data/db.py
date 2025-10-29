from sqlalchemy import create_engine, Column, String, TIMESTAMP, text, Text,Integer, UniqueConstraint, CheckConstraint,ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import declarative_base, sessionmaker,relationship
import uuid

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/biblioteca"
#DATABASE_URL =  "sqlite:///./biblioteca.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(150), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    favorite_books = Column(JSON, default=list)
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    
    avaliacoes = relationship('Avaliacao', back_populates='usuario', cascade='all, delete-orphan')

class Livro(Base):
    __tablename__ = 'livros'
    
    id = Column(Integer, primary_key=True)
    google_books_id = Column(String(50), unique=True, nullable=False, index=True)
    rate = Column(Integer,nullable=False,index=True)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
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
    usuario_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    estrelas = Column(Integer, nullable=False)
    comentario = Column(Text)
    data_avaliacao = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    
    # Relacionamentos
    livro = relationship('Livro', back_populates='avaliacoes')
    usuario = relationship('User', back_populates='avaliacoes')




#def get_db_session():
    #return SessionLocal()






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