from custom_requester.custom_requester import CustomRequester
from constants import MOVIES_ENDPOINT, BASE_URL_MOVIES


class MoviesAPI(CustomRequester):
    """
    Класс для работы с эндпоинтами фильмов (/movies).
    Наследуется от CustomRequester для переиспользования логики запросов.
    """

    def __init__(self, session):
        """
        :param session: requests.Session (передаётся из ApiManager)
        """
        super().__init__(
            session=session,
            base_url=BASE_URL_MOVIES.strip()
        )

    # GET

    def get_movies_list(self, params=None, expected_status=200):
        """
        Получить список фильмов с пагинацией и фильтрами.
        :param params: dict с параметрами (genre, location, published, page, pageSize)
        :param expected_status: ожидаемый статус-код
        """
        return self.send_request(
            method="GET",
            endpoint=MOVIES_ENDPOINT.strip(),
            data=None,
            expected_status=expected_status,
            params=params  # ← Параметры добавятся в URL: ?key=value
        )

    def get_movie_by_id(self, movie_id, expected_status=200):
        """
        Получить фильм по ID.
        :param movie_id: ID фильма (int)
        :param expected_status: ожидаемый статус-код
        """
        return self.send_request(
            method="GET",
            endpoint=f"{MOVIES_ENDPOINT}/{movie_id}",
            data=None,
            expected_status=expected_status
        )

    # POST

    def create_movie(self, movie_data, expected_status=201):
        """
        Создать новый фильм.
        :param movie_data: dict с данными фильма
        :param expected_status: ожидаемый статус-код
        """
        return self.send_request(
            method="POST",
            endpoint=MOVIES_ENDPOINT.strip(),
            data=movie_data,
            expected_status=expected_status
        )

    # PATCH

    def update_movie(self, movie_id, movie_data, expected_status=200):
        """
        Частично обновить фильм (только переданные поля).
        :param movie_id: ID фильма
        :param movie_data: dict с полями для обновления
        :param expected_status: ожидаемый статус-код
        """
        return self.send_request(
            method="PATCH",
            endpoint=f"{MOVIES_ENDPOINT}/{movie_id}",
            data=movie_data,
            expected_status=expected_status
        )

    # DELETE

    def delete_movie(self, movie_id, expected_status=200):
        """
        Удалить фильм.
        :param movie_id: ID фильма
        :param expected_status: ожидаемый статус-код
        """
        return self.send_request(
            method="DELETE",
            endpoint=f"{MOVIES_ENDPOINT}/{movie_id}",
            data=None,
            expected_status=expected_status
        )