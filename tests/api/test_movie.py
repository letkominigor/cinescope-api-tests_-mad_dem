"""Тесты создания и получения фильмов (позитивные сценарии)."""
import pytest
import allure
from api.api_manager import ApiManager
from custom_requester.custom_requester import RequestError
from utils.data_generator import DataGenerator
from constants.constants import STATUS_OK, STATUS_CREATED, STATUS_NOT_FOUND
from models.movie_response import MovieResponse, MoviesListResponse


@allure.feature("Movies API")
@allure.story("Получение и управление фильмами")
@allure.label("qa_name", "Komin Igor")
@allure.label("layer", "api")
class TestMoviesPositive:
    """Позитивные тесты для фильмов."""

    @allure.title("Получение списка всех фильмов")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke
    @pytest.mark.api
    @pytest.mark.positive
    def test_get_movies_list(self, api_manager: ApiManager):
        """Позитивный тест: получение списка фильмов без авторизации."""
        # Act
        with allure.step("Отправляем запрос на получение списка фильмов"):
            response = api_manager.movies_api.get_movies_list(expected_status=STATUS_OK)

        # Assert
        with allure.step("Проверяем структуру ответа"):
            response_data = response.json()
            assert "movies" in response_data, "Ответ должен содержать ключ 'movies'"
            assert "count" in response_data, "Ответ должен содержать ключ 'count'"

        with allure.step("Валидируем схему ответа через Pydantic"):
            movies_response = MoviesListResponse(**response_data)
            assert movies_response.count >= 0
            assert isinstance(movies_response.movies, list)

    @allure.title("Фильтрация фильмов по статусу published")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    @pytest.mark.positive
    def test_get_movies_filtered_by_published(self, api_manager: ApiManager, published_movie):
        """Позитивный тест: фильтрация по published=true."""
        # Act
        with allure.step("Запрашиваем только опубликованные фильмы"):
            response = api_manager.movies_api.get_movies_list(
                params={"published": "true"},
                expected_status=STATUS_OK
            )

        # Assert
        with allure.step("Проверяем, что все фильмы опубликованы"):
            response_data = response.json()
            movies_list = response_data.get("movies", [])
            assert len(movies_list) > 0

            for movie in movies_list:
                assert movie.get("published") is True

        with allure.step("Валидируем схему ответа через Pydantic"):
            movies_response = MoviesListResponse(**response_data)
            for movie in movies_response.movies:
                assert movie.published is True

    @allure.title("Получение фильма по идентификатору")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.api
    @pytest.mark.positive
    def test_get_movie_by_id(self, admin_session: ApiManager):
        """Позитивный тест: получение фильма по его ID."""
        # Arrange
        with allure.step("Создаём тестовый фильм"):
            movie_data = DataGenerator.generate_movie_data()
            create_response = admin_session.movies_api.create_movie(movie_data)
            movie_id = create_response.json()["id"]

        try:
            # Act
            with allure.step(f"Получаем фильм с ID {movie_id}"):
                response = admin_session.movies_api.get_movie_by_id(movie_id, expected_status=STATUS_OK)
                response_data = response.json()

            # Assert
            with allure.step("Проверяем, что данные фильма совпадают"):
                assert response_data["id"] == movie_id
                assert response_data["name"] == movie_data["name"]

            with allure.step("Валидируем схему ответа через Pydantic"):
                movie_response = MovieResponse(**response_data)
                assert movie_response.id == movie_id
                assert movie_response.name == movie_data["name"]

        finally:
            # Cleanup
            with allure.step("Удаляем тестовый фильм"):
                admin_session.movies_api.delete_movie(movie_id, expected_status=STATUS_OK)

    @allure.title("Создание нового фильма")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.api
    @pytest.mark.positive
    def test_create_movie(self, admin_session: ApiManager):
        """Позитивный тест: создание фильма с валидными данными."""
        # Arrange
        with allure.step("Генерируем валидные данные для фильма"):
            movie_data = DataGenerator.generate_movie_data()

        # Act
        with allure.step("Отправляем запрос на создание фильма"):
            create_response = admin_session.movies_api.create_movie(
                movie_data,
                expected_status=STATUS_CREATED
            )
            response_data = create_response.json()
            movie_id = response_data["id"]

        try:
            # Assert
            with allure.step("Проверяем, что ответ содержит все необходимые поля"):
                assert "id" in response_data
                assert response_data["name"] == movie_data["name"]
                assert response_data["location"] == movie_data["location"]
                assert "createdAt" in response_data

            with allure.step("Валидируем схему ответа через Pydantic"):
                movie_response = MovieResponse(**response_data)
                assert movie_response.id == movie_id
                assert movie_response.name == movie_data["name"]

        finally:
            # Cleanup
            with allure.step("Удаляем созданный фильм"):
                admin_session.movies_api.delete_movie(movie_id, expected_status=STATUS_OK)

    def test_update_movie(self, published_movie_with_session):
        movie, api_manager = published_movie_with_session
        movie_id = movie["id"]

        update_data = {
            "name": "Updated Movie Name",
            "description": movie.get("description"),
            "price": movie.get("price"),
            "location": movie.get("location"),
            "imageUrl": movie.get("imageUrl"),
            "published": movie.get("published", True),
            "genreId": movie.get("genreId")
        }
        update_data = {k: v for k, v in update_data.items() if v is not None}

        # Логируем данные для обновления
        print(f"Обновляем фильм {movie_id} с данными: {update_data}")

        try:
            with allure.step(f"Обновляем фильм {movie_id}"):
                response = api_manager.movies_api.update_movie(movie_id, update_data)
                print(f"Статус обновления: {response.status_code}")
                print(f"Ответ сервера: {response.json()}")
        except RequestError as e:
            print(f"Ошибка при обновлении: {e}")
            print(f"Статус: {e.response.status_code}")
            print(f"Ответ: {e.response.json()}")

    @allure.title("Удаление фильма")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.api
    @pytest.mark.positive
    def test_delete_movie(self, admin_session: ApiManager):
        """Позитивный тест: удаление фильма и проверка, что он больше не доступен."""
        # Arrange
        with allure.step("Создаём тестовый фильм для удаления"):
            movie_data = DataGenerator.generate_movie_data()
            create_response = admin_session.movies_api.create_movie(movie_data)
            movie_id = create_response.json()["id"]

        # Act
        with allure.step(f"Удаляем фильм с ID {movie_id}"):
            delete_response = admin_session.movies_api.delete_movie(
                movie_id,
                expected_status=STATUS_OK
            )

        # Assert
        with allure.step("Проверяем статус удаления"):
            assert delete_response.status_code == STATUS_OK

        with allure.step("Проверяем, что фильм больше не доступен"):
            with pytest.raises(RequestError) as exc_info:
                admin_session.movies_api.get_movie_by_id(movie_id, expected_status=STATUS_OK)
            assert exc_info.value.response.status_code == STATUS_NOT_FOUND
