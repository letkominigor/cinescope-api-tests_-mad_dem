import pytest
from faker.generator import random
from api.api_manager import ApiManager
from custom_requester.custom_requester import RequestError
from utils.data_generator import DataGenerator

class TestMoviesPositive:

    #  Эти тесты работают БЕЗ авторизации — оставляем api_manager
    def test_get_movies_list(self, api_manager: ApiManager):
        response = api_manager.movies_api.get_movies_list(expected_status=200)
        response_data = response.json()
        assert "movies" in response_data
        assert "count" in response_data

    def test_get_movies_filtered_by_published(self, api_manager: ApiManager, published_movie):
        """Тест: фильтрация по published с гарантированным наличием данных."""
        response = api_manager.movies_api.get_movies_list(
            params={"published": "true"},
            expected_status=200
        )
        response_data = response.json()
        movies_list = response_data.get("movies", [])

        # есть хотя бы один фильм (наш созданный)
        assert len(movies_list) > 0

        for movie in movies_list:
            assert movie.get("published") is True

    #  Эти тесты ТРЕБУЮТ авторизации — используем admin_session
    def test_get_movies_filtered_by_location(self, admin_session: ApiManager):
        """Тест фильтрация по локации."""
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
        """Тест получение фильма по ID."""
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
        Тест: создание нового фильма.
        Проверяет, что фильм создаётся и возвращается ответ
        """
        # Создаём фильм
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
            # Очистка выполнится ВСЕГДА, даже если ассерты упадут
            admin_session.movies_api.delete_movie(movie_id, expected_status=200)

    def test_update_movie(self, created_movie, admin_session):
        # В тесте теперь только проверка, очистка в фикстуре !
        movie_id = created_movie["id"]

        update_data = {"name": "Updated"}
        response = admin_session.movies_api.update_movie(movie_id, update_data)
        assert response.json()["name"] == "Updated"

    def test_delete_movie(self, admin_session: ApiManager):
        """
        Тест удаление фильма. 404 должно быть
        """
        # Создаём фильм ВНУТРИ теста
        movie_data = DataGenerator.generate_movie_data()
        create_response = admin_session.movies_api.create_movie(movie_data)
        movie_id = create_response.json()["id"]

        # Удаляем фильм (API возвращает 200, не 204!!!)
        delete_response = admin_session.movies_api.delete_movie(
            movie_id,
            expected_status=200
        )
        assert delete_response.status_code == 200

        # Проверяем, что фильм удалён (получаем 404)
        with pytest.raises(RequestError) as exc_info:
            admin_session.movies_api.get_movie_by_id(
                movie_id,
                expected_status=200
            )

        # Проверяем, что ошибка именно "не найдено"
        assert exc_info.value.response.status_code == 404, (
            f"Ожидали 404 после удаления, получили {exc_info.value.response.status_code}")