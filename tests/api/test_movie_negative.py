"""Негативные тесты для Movies API."""
import pytest
import allure
import random
from api.api_manager import ApiManager
from utils.data_generator import DataGenerator
from constants.constants import STATUS_BAD_REQUEST, STATUS_NOT_FOUND


@allure.feature("Movies API")
@allure.story("Валидация данных фильма")
@allure.label("qa_name", "Komin Igor")
@allure.label("layer", "api")
class TestMoviesNegative:
    """Негативные тесты для фильмов."""

    @allure.title("Получение несуществующего фильма")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @pytest.mark.negative
    @pytest.mark.regression
    def test_get_nonexistent_movie(self, admin_session: ApiManager):
        """Негативный тест: получение фильма с несуществующим ID."""
        # Arrange
        fake_id = random.randint(100000, 999999)

        # Act
        with allure.step(f"Пытаемся получить фильм с несуществующим ID {fake_id}"):
            response = admin_session.movies_api.get_movie_by_id(
                fake_id,
                expected_status=STATUS_NOT_FOUND
            )

        # Assert
        with allure.step("Проверяем статус 404"):
            assert response.status_code == STATUS_NOT_FOUND

    @allure.title("Создание фильма с пустым телом запроса")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @pytest.mark.negative
    @pytest.mark.regression
    def test_create_movie_with_empty_body(self, admin_session: ApiManager):
        """Негативный тест: создание фильма с пустым телом."""
        # Act
        with allure.step("Отправляем запрос с пустым телом"):
            response = admin_session.movies_api.create_movie(
                {},
                expected_status=STATUS_BAD_REQUEST
            )

        # Assert
        with allure.step("Проверяем статус 400"):
            assert response.status_code == STATUS_BAD_REQUEST

    @allure.title("Создание фильма без обязательного поля name")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @pytest.mark.negative
    @pytest.mark.regression
    def test_create_movie_missing_required_field(self, admin_session: ApiManager):
        """Негативный тест: создание без обязательного поля."""
        # Arrange
        movie_data = DataGenerator.generate_movie_data()
        del movie_data["name"]

        # Act
        with allure.step("Отправляем запрос без поля name"):
            response = admin_session.movies_api.create_movie(
                movie_data,
                expected_status=STATUS_BAD_REQUEST
            )

        # Assert
        with allure.step("Проверяем статус 400"):
            assert response.status_code == STATUS_BAD_REQUEST

    @allure.title("Обновление несуществующего фильма")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @pytest.mark.negative
    @pytest.mark.regression
    def test_update_nonexistent_movie(self, admin_session: ApiManager):
        """Негативный тест: обновление несуществующего фильма."""
        # Arrange
        fake_id = random.randint(100000, 999999)
        update_data = {"name": "New Name"}

        # Act
        with allure.step(f"Пытаемся обновить фильм с несуществующим ID {fake_id}"):
            response = admin_session.movies_api.update_movie(
                fake_id,
                update_data,
                expected_status=STATUS_NOT_FOUND
            )

        # Assert
        with allure.step("Проверяем статус 404"):
            assert response.status_code == STATUS_NOT_FOUND

    @allure.title("Удаление несуществующего фильма")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @pytest.mark.negative
    @pytest.mark.regression
    def test_delete_nonexistent_movie(self, admin_session: ApiManager):
        """Негативный тест: удаление несуществующего фильма."""
        # Arrange
        fake_id = random.randint(100000, 999999)

        # Act
        with allure.step(f"Пытаемся удалить фильм с несуществующим ID {fake_id}"):
            response = admin_session.movies_api.delete_movie(
                fake_id,
                expected_status=STATUS_NOT_FOUND
            )

        # Assert
        with allure.step("Проверяем статус 404"):
            assert response.status_code == STATUS_NOT_FOUND