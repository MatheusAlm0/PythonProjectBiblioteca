import requests
from exceptions.custom_exceptions import BadRequestException
from data.db import SessionLocal, Avaliacao, User


class BookService:
    GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"

    @staticmethod
    def _format_book(item, include_avaliacoes=False, book_id=None):
        volume_info = item.get("volumeInfo", {})
        image_links = volume_info.get("imageLinks", {})

        book_data = {
            "id": item.get("id", ""),
            "title": volume_info.get("title", "Título não disponível"),
            "subtitle": volume_info.get("subtitle", ""),
            "authors": volume_info.get("authors", []),
            "publisher": volume_info.get("publisher", ""),
            "publishedDate": volume_info.get("publishedDate", ""),
            "description": volume_info.get("description", "Descrição não disponível"),
            "pageCount": volume_info.get("pageCount", 0),
            "categories": volume_info.get("categories", []),
            "averageRating": volume_info.get("averageRating", None),
            "ratingsCount": volume_info.get("ratingsCount", None),
            "language": volume_info.get("language", ""),
            "previewLink": volume_info.get("previewLink", ""),
            "infoLink": volume_info.get("infoLink", ""),
            "imageLinks": {
                "smallThumbnail": image_links.get("smallThumbnail", ""),
                "thumbnail": image_links.get("thumbnail", ""),
                "small": image_links.get("small", ""),
                "medium": image_links.get("medium", ""),
                "large": image_links.get("large", ""),
                "extraLarge": image_links.get("extraLarge", "")
            },
            "industryIdentifiers": volume_info.get("industryIdentifiers", [])
        }

        return book_data

    @staticmethod
    def _get_avaliacoes(google_books_id):
        session = SessionLocal()
        try:
            avaliacoes = session.query(Avaliacao).join(User).filter(
                Avaliacao.google_books_id == google_books_id
            ).order_by(Avaliacao.data_avaliacao.desc()).all()

            return [{
                'usuario_nome': av.usuario.username,
                'estrelas': av.estrelas,
                'comentario': av.comentario,
                'data_avaliacao': av.data_avaliacao.isoformat() if av.data_avaliacao else None
            } for av in avaliacoes]
        except Exception as e:
            print(f"Erro ao buscar avaliações: {e}")
            return []
        finally:
            session.close()

    @staticmethod
    def search_books(query):
        if not query or not query.strip():
            raise BadRequestException("Livro não encontrado.")

        all_books = []
        max_results_per_page = 10
        total_pages = 4

        for page in range(total_pages):
            start_index = page * max_results_per_page
            params = {
                "q": query,
                "maxResults": max_results_per_page,
                "startIndex": start_index
            }

            try:
                response = requests.get(
                    BookService.GOOGLE_BOOKS_API_URL,
                    params=params,
                    timeout=5
                )

                if response.status_code != 200:
                    continue

                data = response.json()
                items = data.get("items", [])

                if not items:
                    break

                all_books.extend(items)

            except requests.exceptions.Timeout:
                continue
            except Exception:
                continue

        return [BookService._format_book(item) for item in all_books]

    @staticmethod
    def search_books_by_id(book_id):
        if not book_id or not book_id.strip():
            raise BadRequestException("O ID do livro é obrigatório.")

        response = requests.get(f"{BookService.GOOGLE_BOOKS_API_URL}/{book_id}")

        if response.status_code == 404:
            raise BadRequestException("Livro não encontrado.")
        if response.status_code != 200:
            raise BadRequestException("Livro não encontrado.")

        book_data = BookService._format_book(response.json())

        avaliacoes = BookService._get_avaliacoes(book_id)

        from collections import OrderedDict
        result = OrderedDict()
        result['book'] = book_data
        result['avaliacoes'] = avaliacoes

        return result