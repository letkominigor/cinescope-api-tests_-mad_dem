"""Негативные тесты для авторизации."""
import pytest
import allure
from api.api_manager import ApiManager
from constants.constants import STATUS_UNAUTHORIZED


@allure.feature("Auth API")
@allure.story("Авторизация пользователя")
@allure.label("qa_name", "Komin Igor")
@allure.label("layer", "api")
class TestAuthNegative:
    """Негативные тесты для авторизации."""

    @allure.title("Авторизация с неверным паролем")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @pytest.mark.negative
    def test_login_with_wrong_password(self, api_manager: ApiManager, registered_user):
        """Тест: авторизация с неверным паролем."""
        # Arrange
        login_data = {
            "email": registered_user.email,
            "password": "WrongPassword123!"
        }

        # Act
        with allure.step("Пытаемся войти с неверным паролем"):
            response = api_manager.auth_api.login_user(
                login_data=login_data,
                expected_status=STATUS_UNAUTHORIZED
            )

        # Assert
        with allure.step("Проверяем статус 401"):
            assert response.status_code == STATUS_UNAUTHORIZED

        with allure.step("Проверяем сообщение об ошибке"):
            response_data = response.json()
            assert "message" in response_data or "error" in response_data

    @allure.title("Авторизация с несуществующим email")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @pytest.mark.negative
    def test_login_with_nonexistent_email(self, api_manager: ApiManager):
        """Тест: авторизация с несуществующим email."""
        # Arrange
        login_data = {
            "email": "nonexistent_user_abc123@test.com",
            "password": "KakoiToPass123!"
        }

        # Act
        with allure.step("Пытаемся войти с несуществующим email"):
            response = api_manager.auth_api.login_user(
                login_data=login_data,
                expected_status=STATUS_UNAUTHORIZED
            )

        # Assert
        with allure.step("Проверяем статус 401"):
            assert response.status_code == STATUS_UNAUTHORIZED

        with allure.step("Проверяем сообщение об ошибке"):
            response_data = response.json()
            assert "message" in response_data or "error" in response_data

    @allure.title("Авторизация с пустым телом запроса")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @pytest.mark.negative
    def test_login_with_empty_body(self, api_manager: ApiManager):
        """Тест: авторизация с пустым телом запроса."""
        # Arrange
        login_data = {}

        # Act
        with allure.step("Пытаемся войти с пустым телом запроса"):
            response = api_manager.auth_api.login_user(
                login_data=login_data,
                expected_status=STATUS_UNAUTHORIZED
            )

        # Assert
        with allure.step("Проверяем статус 401"):
            assert response.status_code == STATUS_UNAUTHORIZED

        with allure.step("Проверяем сообщение об ошибке"):
            response_data = response.json()
            assert "message" in response_data or "error" in response_data

    @allure.title("Авторизация с пустым email")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @pytest.mark.negative
    def test_login_with_empty_email(self, api_manager: ApiManager, registered_user):
        """Тест: авторизация с пустым email."""
        # Arrange
        login_data = {
            "email": "",
            "password": registered_user.password
        }

        # Act
        with allure.step("Пытаемся войти с пустым email"):
            response = api_manager.auth_api.login_user(
                login_data=login_data,
                expected_status=STATUS_UNAUTHORIZED
            )

        # Assert
        with allure.step("Проверяем статус 401"):
            assert response.status_code == STATUS_UNAUTHORIZED

    @allure.title("Авторизация с пустым паролем")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @pytest.mark.negative
    def test_login_with_empty_password(self, api_manager: ApiManager, registered_user):
        """Тест: авторизация с пустым паролем."""
        # Arrange
        login_data = {
            "email": registered_user.email,
            "password": ""
        }

        # Act
        with allure.step("Пытаемся войти с пустым паролем"):
            response = api_manager.auth_api.login_user(
                login_data=login_data,
                expected_status=STATUS_UNAUTHORIZED
            )

        # Assert
        with allure.step("Проверяем статус 401"):
            assert response.status_code == STATUS_UNAUTHORIZED