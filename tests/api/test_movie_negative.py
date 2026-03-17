import pytest
from api.api_manager import ApiManager
from custom_requester.custom_requester import RequestError
from utils.data_generator import DataGenerator


class TestMoviesNegative:
    """Негативные тесты для эндпоинта /movies."""

    # GET /movies/{id}

    def test_get_nonexistent_movie(self, admin_session: ApiManager):
        """Тест: получение несуществующего фильма."""
        fake_id = 999999999

        with pytest.raises(RequestError) as exc_info:
            admin_session.movies_api.get_movie_by_id(fake_id, expected_status=200)

        assert exc_info.value.response.status_code in [404, 400, 500]

    # POST /movies

    @pytest.mark.parametrize("invalid_field", ["name", "price", "location", "genreId"])
    def test_create_movie_with_invalid_data(self, admin_session: ApiManager, invalid_field):
        """Тест: создание фильма с невалидными данными."""
        invalid_data = DataGenerator.generate_invalid_movie_data(invalid_field)

        with pytest.raises(RequestError) as exc_info:
            admin_session.movies_api.create_movie(invalid_data, expected_status=201)

        assert exc_info.value.response.status_code in [400, 401, 500]

    def test_create_movie_with_empty_body(self, admin_session: ApiManager):
        """Тест: создание фильма с пустым телом."""
        with pytest.raises(RequestError) as exc_info:
            admin_session.movies_api.create_movie({}, expected_status=201)

        assert exc_info.value.response.status_code in [400, 401, 500]

    def test_create_movie_missing_required_field(self, admin_session: ApiManager):
        """Тест: создание без обязательного поля."""
        movie_data = DataGenerator.generate_movie_data()
        del movie_data["name"]

        with pytest.raises(RequestError) as exc_info:
            admin_session.movies_api.create_movie(movie_data, expected_status=201)

        assert exc_info.value.response.status_code in [400, 401, 500]

    # PATCH /movies/{id}

    def test_update_nonexistent_movie(self, admin_session: ApiManager):
        """Тест: обновление несуществующего фильма."""
        fake_id = 999999999
        update_data = {"name": "New Name"}

        with pytest.raises(RequestError) as exc_info:
            admin_session.movies_api.update_movie(fake_id, update_data, expected_status=200)

        assert exc_info.value.response.status_code in [404, 400, 500]

    # DELETE /movies/{id}

    def test_delete_nonexistent_movie(self, admin_session: ApiManager):
        """Тест: удаление несуществующего фильма."""
        fake_id = 999999999

        with pytest.raises(RequestError) as exc_info:
            admin_session.movies_api.delete_movie(fake_id, expected_status=200)

        assert exc_info.value.response.status_code in [404, 400, 500]