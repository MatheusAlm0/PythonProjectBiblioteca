from typing import Optional, Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from data.db import Livro, Avaliacao, User

class RatingService:
    
    def __init__(self, db_session: Session):
        """
        Args:
            db_session: Sessão do SQLAlchemy
        """
        self.db = db_session
    
    @staticmethod
    def _validar_estrelas(estrelas: int) -> bool:
        """Valida se estrelas está entre 1 e 5"""
        return isinstance(estrelas, int) and 1 <= estrelas <= 5
    
    def buscar_ou_criar_livro(self, google_books_id: str, dados_livro: Dict) -> Optional[int]:
        """
        Busca livro no banco ou cria se não existir
        Args:
            google_books_id: ID do Google Books
            dados_livro: Dados do livro vindos da API (já formatados)
        Returns: ID local do livro no banco
        """
        try:
            # 1. Verificar se livro já existe
            livro = self.db.query(Livro).filter_by(google_books_id=google_books_id).first()
            
            if livro:
                return livro.id
            
            # 2. Se não existe, criar
            novo_livro = Livro(
                google_books_id=google_books_id,
                titulo=dados_livro.get('title', ''),
                subtitulo=dados_livro.get('subtitle', ''),
                autores=','.join(dados_livro.get('authors', [])),
                editora=dados_livro.get('publisher', ''),
                data_publicacao=dados_livro.get('publishedDate', ''),
                descricao=dados_livro.get('description', ''),
                num_paginas=dados_livro.get('pageCount', 0),
                categorias=','.join(dados_livro.get('categories', [])),
                idioma=dados_livro.get('language', ''),
                thumbnail_url=dados_livro.get('imageLinks', {}).get('thumbnail', ''),
                preview_link=dados_livro.get('previewLink', ''),
                info_link=dados_livro.get('infoLink', '')
            )
            
            self.db.add(novo_livro)
            self.db.commit()
            self.db.refresh(novo_livro)
            
            return novo_livro.id
            
        except Exception as e:
            self.db.rollback()
            print(f"Erro ao buscar/criar livro: {e}")
            return None
    
    def adicionar_avaliacao(self, google_books_id: str, usuario_id: int, 
                           estrelas: int, comentario: Optional[str] = None) -> bool:
        """
        Adiciona ou atualiza uma avaliação
        Args:
            google_books_id: ID do livro no Google Books
            usuario_id: ID do usuário
            estrelas: Nota de 1 a 5
            comentario: Comentário opcional
        Returns: True se sucesso
        """
        if not self._validar_estrelas(estrelas):
            raise ValueError("Estrelas deve ser um número entre 1 e 5")
        
        try:
            # 1. Buscar dados do livro na API do Google Books
            from services.book_service import BookService
            livros = BookService.search_books_by_id(google_books_id)
            
            if not livros:
                return False
            
            dados_livro = livros[0]
            
            # 2. Buscar ou criar livro no banco
            livro_id = self.buscar_ou_criar_livro(google_books_id, dados_livro)
            if not livro_id:
                return False
            
            # 3. Verificar se já existe avaliação
            avaliacao_existente = self.db.query(Avaliacao).filter_by(
                livro_id=livro_id,
                usuario_id=usuario_id
            ).first()
            
            if avaliacao_existente:
                # Atualizar
                avaliacao_existente.estrelas = estrelas
                avaliacao_existente.comentario = comentario
                avaliacao_existente.data_avaliacao = func.now()
            else:
                # Criar nova
                nova_avaliacao = Avaliacao(
                    livro_id=livro_id,
                    usuario_id=usuario_id,
                    estrelas=estrelas,
                    comentario=comentario
                )
                self.db.add(nova_avaliacao)
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            print(f"Erro ao adicionar avaliação: {e}")
            return False
    
    def remover_avaliacao(self, google_books_id: str, usuario_id: int) -> bool:
        """Remove uma avaliação"""
        try:
            livro = self.db.query(Livro).filter_by(google_books_id=google_books_id).first()
            
            if not livro:
                return False
            
            avaliacao = self.db.query(Avaliacao).filter_by(
                livro_id=livro.id,
                usuario_id=usuario_id
            ).first()
            
            if avaliacao:
                self.db.delete(avaliacao)
                self.db.commit()
                return True
            
            return False
            
        except Exception as e:
            self.db.rollback()
            print(f"Erro ao remover avaliação: {e}")
            return False
    
    def obter_estatisticas(self, google_books_id: str) -> Optional[Dict]:
        """
        Retorna estatísticas de avaliações de um livro
        """
        try:
            livro = self.db.query(Livro).filter_by(google_books_id=google_books_id).first()
            
            if not livro:
                return None
            
            # Calcular média e total
            stats = self.db.query(
                func.avg(Avaliacao.estrelas).label('media'),
                func.count(Avaliacao.id).label('total')
            ).filter(Avaliacao.livro_id == livro.id).first()
            
            # Distribuição por estrelas
            distribuicao_query = self.db.query(
                Avaliacao.estrelas,
                func.count(Avaliacao.id).label('quantidade')
            ).filter(Avaliacao.livro_id == livro.id).group_by(Avaliacao.estrelas).all()
            
            distribuicao = {row[0]: row[1] for row in distribuicao_query}
            
            return {
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
            print(f"Erro ao obter estatísticas: {e}")
            return None
    
    def obter_avaliacoes(self, google_books_id: str, limite: int = 10) -> List[Dict]:
        """Lista as avaliações mais recentes de um livro"""
        try:
            livro = self.db.query(Livro).filter_by(google_books_id=google_books_id).first()
            
            if not livro:
                return []
            
            avaliacoes = self.db.query(Avaliacao).join(User).filter(
                Avaliacao.livro_id == livro.id
            ).order_by(Avaliacao.data_avaliacao.desc()).limit(limite).all()
            
            return [{
                'id': av.id,
                'usuario_id': av.usuario_id,
                'usuario_nome': av.usuario.username,
                'estrelas': av.estrelas,
                'comentario': av.comentario,
                'data_avaliacao': av.data_avaliacao.isoformat() if av.data_avaliacao else None
            } for av in avaliacoes]
            
        except Exception as e:
            print(f"Erro ao obter avaliações: {e}")
            return []
    
    def usuario_ja_avaliou(self, google_books_id: str, usuario_id: int) -> bool:
        """Verifica se usuário já avaliou o livro"""
        try:
            livro = self.db.query(Livro).filter_by(google_books_id=google_books_id).first()
            
            if not livro:
                return False
            
            existe = self.db.query(Avaliacao).filter_by(
                livro_id=livro.id,
                usuario_id=usuario_id
            ).first()
            
            return existe is not None
            
        except Exception as e:
            print(f"Erro ao verificar avaliação: {e}")
            return False