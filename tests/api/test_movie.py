import pytest
from faker.generator import random
from api.api_manager import ApiManager
from custom_requester.custom_requester import RequestError
from utils.data_generator import DataGenerator

class TestMoviesPositive:

    def test_get_movies_list(self, api_manager: ApiManager):
        response = api_manager.movies_api.get_movies_list(expected_status=200)
        response_data = response.json()
        assert "movies" in response_data
        assert "count" in response_data

    def test_get_movies_filtered_by_published(self, api_manager: ApiManager, published_movie):
        """Фильтрация по published """
        response = api_manager.movies_api.get_movies_list(
            params={"published": "true"},
            expected_status=200
        )
        response_data = response.json()
        movies_list = response_data.get("movies", [])

        assert len(movies_list) > 0

        for movie in movies_list:
            assert movie.get("published") is True

    #  Эти тесты ТРЕБУЮТ авторизации
    def test_get_movies_filtered_by_location(self, admin_session: ApiManager):
        """Фильтрация по локации."""
        unique_name = f"FilterTest_{random.randint(10000, 99999)}"
        unique_location = random.choice(["MSK", "SPB"])

        movie_data = DataGenerator.generate_movie_data(
            name=unique_name,
            location=unique_location
        )

        create_response = admin_session.movies_api.create_movie(movie_data)
        movie_id = create_response.json()["id"]

        try:
            response = admin_session.movies_api.get_movie_by_id(
                movie_id,
                expected_status=200
            )
            response_data = response.json()

            assert response_data["location"] == unique_location
            assert response_data["name"] == unique_name

        finally:
            admin_session.movies_api.delete_movie(movie_id, expected_status=200)

    def test_get_movie_by_id(self, admin_session: ApiManager):
        """Получение фильма по ID."""
        movie_data = DataGenerator.generate_movie_data()
        create_response = admin_session.movies_api.create_movie(movie_data)
        movie_id = create_response.json()["id"]

        try:
            response = admin_session.movies_api.get_movie_by_id(movie_id, expected_status=200)
            response_data = response.json()
            assert response_data["id"] == movie_id
            assert response_data["name"] == movie_data["name"]
        finally:
            admin_session.movies_api.delete_movie(movie_id, expected_status=200)

    def test_create_movie(self, admin_session: ApiManager):
        """
        Создание нового фильма.
        Проверяет, что фильм создаётся и возвращается ответ
        """
        movie_data = DataGenerator.generate_movie_data()
        create_response = admin_session.movies_api.create_movie(movie_data, expected_status=201)
        response_data = create_response.json()

        movie_id = response_data["id"]

        try:
            assert "id" in response_data, "Ответ должен содержать ID фильма"
            assert response_data["name"] == movie_data["name"], \
                f"Название фильма не совпадает: ожидалось '{movie_data['name']}', получено '{response_data['name']}'"

            assert response_data["location"] == movie_data["location"], "Локация должна совпадать"
            assert "createdAt" in response_data, "Ответ должен содержать createdAt"

        finally:
            admin_session.movies_api.delete_movie(movie_id, expected_status=200)

    def test_update_movie(self, created_movie, admin_session):
        movie_id = created_movie["id"]

        update_data = {"name": "Updated"}
        response = admin_session.movies_api.update_movie(movie_id, update_data)
        assert response.json()["name"] == "Updated"

    def test_delete_movie(self, admin_session: ApiManager):
        """
        Тест удаление фильма. 404 должно быть
        """
        movie_data = DataGenerator.generate_movie_data()
        create_response = admin_session.movies_api.create_movie(movie_data)
        movie_id = create_response.json()["id"]

        delete_response = admin_session.movies_api.delete_movie(
            movie_id,
            expected_status=200
        )
        assert delete_response.status_code == 200

        with pytest.raises(RequestError) as exc_info:
            admin_session.movies_api.get_movie_by_id(
                movie_id,
                expected_status=200
            )

        assert exc_info.value.response.status_code == 404, (
            f"Ожидали 404 после удаления, получили {exc_info.value.response.status_code}")