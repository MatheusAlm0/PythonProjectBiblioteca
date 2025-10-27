from sqlalchemy import create_engine, Column, String, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
import uuid

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/biblioteca"

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