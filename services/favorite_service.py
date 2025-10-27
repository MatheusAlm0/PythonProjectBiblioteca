from data.db import SessionLocal, User
from exceptions.custom_exceptions import BadRequestException
from sqlalchemy.orm.attributes import flag_modified


class FavoriteService:

    @staticmethod
    def add_favorite(user_id, book_id):
        if not user_id or not user_id.strip():
            raise BadRequestException("O ID do usuário é obrigatório.")

        if not book_id or not book_id.strip():
            raise BadRequestException("O ID do livro é obrigatório.")

        if ',' in book_id:
            book_ids = [bid.strip() for bid in book_id.split(',') if bid.strip()]
        else:
            book_ids = [book_id]

        unique_book_ids = list(set(book_ids))
        if len(unique_book_ids) < len(book_ids):
            duplicates = [bid for bid in book_ids if book_ids.count(bid) > 1]
            raise BadRequestException(f"IDs duplicados no request: {', '.join(set(duplicates))}")

        session = SessionLocal()
        try:
            user = session.query(User).filter_by(id=user_id).first()

            if not user:
                raise BadRequestException("Usuário não encontrado.")

            if user.favorite_books is None:
                user.favorite_books = []

            already_in = [bid for bid in unique_book_ids if bid in user.favorite_books]
            if already_in:
                raise BadRequestException(f"Livros já nos favoritos: {', '.join(already_in)}")

            user.favorite_books.extend(unique_book_ids)

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

            user.favorite_books.remove(book_id)

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
