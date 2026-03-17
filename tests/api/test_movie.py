import pytest
from faker.generator import random
from api.api_manager import ApiManager
from utils.data_generator import DataGenerator

class TestMoviesPositive:

    #  Эти тесты работают БЕЗ авторизации — оставляем api_manager
    def test_get_movies_list(self, api_manager: ApiManager):
        response = api_manager.movies_api.get_movies_list(expected_status=200)
        response_data = response.json()
        assert "movies" in response_data
        assert "count" in response_data

    def test_get_movies_filtered_by_published(self, api_manager: ApiManager):
        response = api_manager.movies_api.get_movies_list(
            params={"published": "true"},
            expected_status=200
        )
        response_data = response.json()
        for movie in response_data.get("movies", []):
            assert movie.get("published") is True

    #  Эти тесты ТРЕБУЮТ авторизации — используем admin_session
    def test_get_movies_filtered_by_location(self, admin_session: ApiManager):
        """Тест: фильтрация по локации."""
        #  Уникальное название для лёгкого поиска
        unique_name = f"FilterTest_{random.randint(10000, 99999)}"
        unique_location = random.choice(["MSK", "SPB"])

        movie_data = DataGenerator.generate_movie_data(
            name=unique_name,
            location=unique_location
        )

        create_response = admin_session.movies_api.create_movie(movie_data)
        movie_id = create_response.json()["id"]

        try:
            #  Проверяем через GET by ID (гарантированно найдёт)
            response = admin_session.movies_api.get_movie_by_id(movie_id, expected_status=200)
            response_data = response.json()

            assert response_data["location"] == unique_location
            assert response_data["name"] == unique_name

        finally:
            admin_session.movies_api.delete_movie(movie_id, expected_status=200)

    def test_get_movie_by_id(self, admin_session: ApiManager):
        """Тест: получение фильма по ID."""
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
        """Тест: создание нового фильма."""
        movie_data = DataGenerator.generate_movie_data()
        response = admin_session.movies_api.create_movie(movie_data, expected_status=201)
        response_data = response.json()

        assert "id" in response_data
        assert response_data["name"] == movie_data["name"]

        # Очистка
        admin_session.movies_api.delete_movie(response_data["id"], expected_status=200)

    def test_update_movie_partial(self, admin_session: ApiManager):
        """Тест: частичное обновление фильма."""
        original_data = DataGenerator.generate_movie_data()
        create_response = admin_session.movies_api.create_movie(original_data)
        movie_id = create_response.json()["id"]

        try:
            update_data = {"name": "Updated Movie Name"}
            response = admin_session.movies_api.update_movie(
                movie_id=movie_id,
                movie_data=update_data,
                expected_status=200
            )
            response_data = response.json()
            assert response_data["name"] == "Updated Movie Name"
        finally:
            admin_session.movies_api.delete_movie(movie_id, expected_status=200)

    def test_delete_movie(self, admin_session: ApiManager):
        """Тест: удаление фильма."""
        movie_data = DataGenerator.generate_movie_data()
        create_response = admin_session.movies_api.create_movie(movie_data)
        movie_id = create_response.json()["id"]

        # Удаляем
        delete_response = admin_session.movies_api.delete_movie(movie_id, expected_status=200)
        assert delete_response.status_code == 200

        # Проверяем, что фильм удалён
        with pytest.raises(Exception):
            admin_session.movies_api.get_movie_by_id(movie_id, expected_status=200)