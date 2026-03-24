"""API класс для работы с фильмами."""
from constants.constants import MOVIES_ENDPOINT, BASE_URL_MOVIES
from custom_requester.custom_requester import CustomRequester


class MoviesAPI(CustomRequester):
    """Класс для работы с эндпоинтами фильмов (/movies)."""

    def __init__(self, session):
        """Инициализация MoviesAPI."""
        super().__init__(
            session=session,
            base_url=BASE_URL_MOVIES.strip()
        )

    def get_movies_list(self, params=None, expected_status=200):
        """Получить список фильмов с пагинацией и фильтрами."""
        return self.send_request(
            method="GET",
            endpoint=MOVIES_ENDPOINT.strip(),
            data=None,
            expected_status=expected_status,
            params=params
        )

    def get_movie_by_id(self, movie_id, expected_status=200):
        """Получить фильм по ID."""
        return self.send_request(
            method="GET",
            endpoint=f"{MOVIES_ENDPOINT.strip()}/{movie_id}",
            data=None,
            expected_status=expected_status
        )

    def create_movie(self, movie_data, expected_status=201):
        """Создать новый фильм."""
        return self.send_request(
            method="POST",
            endpoint=MOVIES_ENDPOINT.strip(),
            data=movie_data,
            expected_status=expected_status
        )

    def update_movie(self, movie_id, movie_data, expected_status=200):
        """Частично обновить фильм."""
        return self.send_request(
            method="PATCH",
            endpoint=f"{MOVIES_ENDPOINT.strip()}/{movie_id}",
            data=movie_data,
            expected_status=expected_status
        )

    def delete_movie(self, movie_id, expected_status=200):
        """
        Удалить фильм.

        :param movie_id: ID фильма
        :param expected_status: Ожидаемый статус-код (200, не 204!)
        """
        return self.send_request(
            method="DELETE",
            endpoint=f"{MOVIES_ENDPOINT.strip()}/{movie_id}",
            data=None,
            expected_status=expected_status
        )