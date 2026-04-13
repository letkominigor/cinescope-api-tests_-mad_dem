"""Тесты управления пользователями."""
import pytest
import allure
from constants.constants import STATUS_FORBIDDEN


@allure.feature("User API")
@allure.story("Управление пользователями")
@allure.label("qa_name", "Komin Igor")
@allure.label("layer", "api")
class TestUser:
    """Тесты для эндпоинтов управления пользователями."""

    @allure.title("Создание нового пользователя")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.api
    @pytest.mark.positive
    def test_create_user(self, super_admin, creation_user_data):
        """Создание пользователя супер-админом"""
        # Act
        with allure.step("Отправляем запрос на создание пользователя"):
            response = super_admin.api.user_api.create_user(creation_user_data)
            response_data = response.json()

        # Assert
        with allure.step("Проверяем, что ответ содержит все необходимые поля"):
            assert response_data.get("id") and response_data["id"] != "", "ID должен быть не пустым"
            assert response_data.get("email") == creation_user_data["email"]
            assert response_data.get("fullName") == creation_user_data["fullName"]
            assert response_data.get("roles", []) == creation_user_data["roles"]
            assert response_data.get("verified") is True

    @allure.title("Получение пользователя по ID и email")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.api
    @pytest.mark.positive
    def test_get_user_by_locator(self, super_admin, creation_user_data):
        """Получение пользователя по разным локаторам"""
        # Arrange
        with allure.step("Создаём тестового пользователя"):
            created_user_response = super_admin.api.user_api.create_user(creation_user_data).json()
            user_id = created_user_response["id"]

        # Act
        with allure.step("Получаем пользователя по ID"):
            response_by_id = super_admin.api.user_api.get_user(user_id).json()

        with allure.step("Получаем пользователя по email"):
            response_by_email = super_admin.api.user_api.get_user(creation_user_data["email"]).json()

        # Assert
        with allure.step("Сравниваем ответы — они должны быть идентичны"):
            assert response_by_id == response_by_email, "Содержание ответов должно быть идентичным"

        with allure.step("Проверяем поля пользователя"):
            assert response_by_id.get("id") and response_by_id["id"] != "", "ID должен быть не пустым"
            assert response_by_id.get("email") == creation_user_data["email"]
            assert response_by_id.get("fullName") == creation_user_data["fullName"]
            assert response_by_id.get("roles", []) == creation_user_data["roles"]
            assert response_by_id.get("verified") is True

    @allure.title("Получение пользователя обычным пользователем (доступ запрещён)")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    @pytest.mark.roles
    @pytest.mark.negative
    @pytest.mark.slow
    def test_get_user_by_id_common_user(self, common_user):
        """Обычный пользователь не может получать других пользователей"""
        # Act & Assert
        with allure.step("Обычный пользователь пытается получить данные пользователя"):
            response = common_user.api.user_api.get_user(
                common_user.email,
                expected_status=STATUS_FORBIDDEN
            )
            assert response.status_code == STATUS_FORBIDDEN


