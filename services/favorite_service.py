from data.db import SessionLocal, User
from exceptions.custom_exceptions import BadRequestException
from sqlalchemy.orm.attributes import flag_modified


class FavoriteService:

    @staticmethod
    def add_favorite(user_id, book_id):
        """Adiciona um ou mais livros aos favoritos do usuário"""
        if not user_id or not user_id.strip():
            raise BadRequestException("O ID do usuário é obrigatório.")

        if not book_id or not book_id.strip():
            raise BadRequestException("O ID do livro é obrigatório.")

        # Se book_id contém vírgulas, trata como múltiplos IDs
        if ',' in book_id:
            book_ids = [bid.strip() for bid in book_id.split(',') if bid.strip()]
        else:
            book_ids = [book_id]

        # Verifica duplicatas na entrada
        unique_book_ids = list(set(book_ids))
        if len(unique_book_ids) < len(book_ids):
            duplicates = [bid for bid in book_ids if book_ids.count(bid) > 1]
            raise BadRequestException(f"IDs duplicados no request: {', '.join(set(duplicates))}")

        session = SessionLocal()
        try:
            user = session.query(User).filter_by(id=user_id).first()

            if not user:
                raise BadRequestException("Usuário não encontrado.")

            # Inicializa lista se for None
            if user.favorite_books is None:
                user.favorite_books = []

            # Verifica se algum livro já está nos favoritos
            already_in = [bid for bid in unique_book_ids if bid in user.favorite_books]
            if already_in:
                raise BadRequestException(f"Livros já nos favoritos: {', '.join(already_in)}")

            # Adiciona os livros
            user.favorite_books.extend(unique_book_ids)

            # Marca a coluna como modificada (necessário para JSON no PostgreSQL)
            flag_modified(user, "favorite_books")
            session.commit()

            return {
                "message": f"Livros adicionados com sucesso: {', '.join(unique_book_ids)}"
            }
        except BadRequestException:
            raise
        except Exception as e:
            session.rollback()
            raise Exception(f"Erro ao adicionar favorito: {str(e)}")
        finally:
            session.close()

    @staticmethod
    def remove_favorite(user_id, book_id):
        """Remove um livro dos favoritos do usuário"""
        if not user_id or not user_id.strip():
            raise BadRequestException("O ID do usuário é obrigatório.")

        if not book_id or not book_id.strip():
            raise BadRequestException("O ID do livro é obrigatório.")

        session = SessionLocal()
        try:
            user = session.query(User).filter_by(id=user_id).first()

            if not user:
                raise BadRequestException("Usuário não encontrado.")

            if user.favorite_books is None or book_id not in user.favorite_books:
                raise BadRequestException("Livro não encontrado nos favoritos.")

            # Remove o livro dos favoritos
            user.favorite_books.remove(book_id)

            # Marca a coluna como modificada
            flag_modified(user, "favorite_books")

            session.commit()

            return {
                "message": "Livro removido dos favoritos com sucesso!"
            }
        except BadRequestException:
            raise
        except Exception as e:
            session.rollback()
            raise Exception(f"Erro ao remover favorito: {str(e)}")
        finally:
            session.close()

    @staticmethod
    def get_favorites(user_id):
        """Retorna todos os IDs dos livros favoritos do usuário"""
        if not user_id or not user_id.strip():
            raise BadRequestException("O ID do usuário é obrigatório.")

        session = SessionLocal()
        try:
            user = session.query(User).filter_by(id=user_id).first()

            if not user:
                raise BadRequestException("Usuário não encontrado.")

            return {
                "total": len(user.favorite_books or []),
                "favorite_books": user.favorite_books or []
            }
        finally:
            session.close()

    @staticmethod
    def is_favorite(user_id, book_id):
        """Verifica se um livro está nos favoritos do usuário"""
        if not user_id or not user_id.strip():
            raise BadRequestException("O ID do usuário é obrigatório.")

        if not book_id or not book_id.strip():
            raise BadRequestException("O ID do livro é obrigatório.")

        session = SessionLocal()
        try:
            user = session.query(User).filter_by(id=user_id).first()

            if not user:
                raise BadRequestException("Usuário não encontrado.")

            return book_id in (user.favorite_books or [])
        finally:
            session.close()
