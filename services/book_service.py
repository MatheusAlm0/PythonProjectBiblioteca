import requests
from services.validation_service import ValidationService

class BookService:
    GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"

    @staticmethod
    def search_books(query):
        ValidationService.validate_search_query(query)
        params = {"q": query, "maxResults": 10}
        response = requests.get(BookService.GOOGLE_BOOKS_API_URL, params=params)
        if response.status_code != 200:
            raise Exception("Erro ao consultar a API do Google Books.")
        data = response.json()
        books = []
        for item in data.get("items", []):
            volume_info = item.get("volumeInfo", {})
            industry_identifiers = volume_info.get("industryIdentifiers", [])
            image_links = volume_info.get("imageLinks", {})
            books.append({
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
                "industryIdentifiers": industry_identifiers
            })
        return books
