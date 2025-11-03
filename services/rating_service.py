from typing import Optional, Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from data.db import Avaliacao, User
from exceptions.custom_exceptions import BadRequestException


class RatingService:

    def __init__(self, db_session: Session):
        self.db = db_session

    @staticmethod
    def _validar_estrelas(estrelas: int) -> bool:
        return isinstance(estrelas, int) and 1 <= estrelas <= 5

    def adicionar_avaliacao(self, google_books_id: str, usuario_id: str,
                            estrelas: int, comentario: Optional[str] = None) -> Dict:
        if not self._validar_estrelas(estrelas):
            raise ValueError("Estrelas deve ser um número entre 1 e 5")

        if not google_books_id or not google_books_id.strip():
            raise BadRequestException("O ID do livro é obrigatório.")

        try:
            usuario = self.db.query(User).filter_by(id=usuario_id).first()
            if not usuario:
                raise BadRequestException("Usuário não encontrado.")

            avaliacao_existente = self.db.query(Avaliacao).filter_by(
                google_books_id=google_books_id,
                usuario_id=usuario_id
            ).first()

            if avaliacao_existente:
                avaliacao_existente.estrelas = estrelas
                avaliacao_existente.comentario = comentario
                mensagem = "Avaliação atualizada com sucesso!"
            else:
                nova_avaliacao = Avaliacao(
                    google_books_id=google_books_id,
                    usuario_id=usuario_id,
                    estrelas=estrelas,
                    comentario=comentario
                )
                self.db.add(nova_avaliacao)
                mensagem = "Avaliação adicionada com sucesso!"

            self.db.commit()
            return {"message": mensagem}

        except BadRequestException:
            raise
        except ValueError:
            raise
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Erro ao adicionar avaliação: {str(e)}")

    def remover_avaliacao(self, google_books_id: str, usuario_id: str) -> bool:
        try:
            avaliacao = self.db.query(Avaliacao).filter_by(
                google_books_id=google_books_id,
                usuario_id=usuario_id
            ).first()

            if avaliacao:
                self.db.delete(avaliacao)
                self.db.commit()
                return True

            return False

        except Exception as e:
            self.db.rollback()
            raise Exception(f"Erro ao remover avaliação: {str(e)}")

    def obter_estatisticas(self, google_books_id: str) -> Optional[Dict]:
        try:
            stats = self.db.query(
                func.avg(Avaliacao.estrelas).label('media'),
                func.count(Avaliacao.id).label('total')
            ).filter(Avaliacao.google_books_id == google_books_id).first()

            if stats.total == 0:
                return None

            distribuicao_query = self.db.query(
                Avaliacao.estrelas,
                func.count(Avaliacao.id).label('quantidade')
            ).filter(
                Avaliacao.google_books_id == google_books_id
            ).group_by(Avaliacao.estrelas).all()

            distribuicao = {row[0]: row[1] for row in distribuicao_query}

            return {
                'google_books_id': google_books_id,
                'media': round(stats.media, 1) if stats.media else 0,
                'total_avaliacoes': stats.total,
                'distribuicao': {
                    5: distribuicao.get(5, 0),
                    4: distribuicao.get(4, 0),
                    3: distribuicao.get(3, 0),
                    2: distribuicao.get(2, 0),
                    1: distribuicao.get(1, 0)
                }
            }
        except Exception as e:
            raise Exception(f"Erro ao obter estatísticas: {str(e)}")

    def obter_avaliacoes(self, google_books_id: str, limite: int = 10) -> List[Dict]:
        try:
            avaliacoes = self.db.query(Avaliacao).join(User).filter(
                Avaliacao.google_books_id == google_books_id
            ).order_by(Avaliacao.data_avaliacao.desc()).limit(limite).all()

            return [{
                'id': str(av.id),
                'usuario_id': str(av.usuario_id),
                'usuario_nome': av.usuario.username,
                'estrelas': av.estrelas,
                'comentario': av.comentario,
                'data_avaliacao': av.data_avaliacao.isoformat() if av.data_avaliacao else None
            } for av in avaliacoes]

        except Exception as e:
            raise Exception(f"Erro ao obter avaliações: {str(e)}")

    def obter_avaliacoes_usuario(self, usuario_id: str) -> List[Dict]:
        """Obter todas as avaliações de um usuário específico"""
        try:
            avaliacoes = self.db.query(Avaliacao).filter(
                Avaliacao.usuario_id == usuario_id
            ).order_by(Avaliacao.data_avaliacao.desc()).all()

            return [{
                'id': str(av.id),
                'google_books_id': av.google_books_id,
                'estrelas': av.estrelas,
                'comentario': av.comentario,
                'data_avaliacao': av.data_avaliacao.isoformat() if av.data_avaliacao else None
            } for av in avaliacoes]

        except Exception as e:
            raise Exception(f"Erro ao obter avaliações do usuário: {str(e)}")

    def usuario_ja_avaliou(self, google_books_id: str, usuario_id: str) -> Dict:
        try:
            avaliacao = self.db.query(Avaliacao).filter_by(
                google_books_id=google_books_id,
                usuario_id=usuario_id
            ).first()

            if avaliacao:
                return {
                    'ja_avaliou': True,
                    'avaliacao': {
                        'id': str(avaliacao.id),
                        'estrelas': avaliacao.estrelas,
                        'comentario': avaliacao.comentario,
                        'data_avaliacao': avaliacao.data_avaliacao.isoformat() if avaliacao.data_avaliacao else None
                    }
                }

            return {'ja_avaliou': False}

        except Exception as e:
            raise Exception(f"Erro ao verificar avaliação: {str(e)}")