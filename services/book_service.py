import requests
from exceptions.custom_exceptions import BadRequestException


class BookService:
    GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"

    @staticmethod
    def _format_book(item):
        volume_info = item.get("volumeInfo", {})
        image_links = volume_info.get("imageLinks", {})

        return {
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

    @staticmethod
    def search_books(query):
        if not query or not query.strip():
            raise BadRequestException("O campo 'findBook' é obrigatório e não pode estar vazio.")

        response = requests.get(
            BookService.GOOGLE_BOOKS_API_URL,
            params={"q": query, "maxResults": 10}
        )

        if response.status_code != 200:
            raise Exception("Erro ao consultar a API do Google Books.")

        data = response.json()
        return [BookService._format_book(item) for item in data.get("items", [])]

    @staticmethod
    def search_books_by_id(book_id):
        if not book_id or not book_id.strip():
            raise BadRequestException("O ID do livro é obrigatório.")

        response = requests.get(f"{BookService.GOOGLE_BOOKS_API_URL}/{book_id}")

        if response.status_code == 404:
            raise BadRequestException("Livro não encontrado.")
        if response.status_code != 200:
            raise Exception("Erro ao consultar a API do Google Books.")

        return [BookService._format_book(response.json())]