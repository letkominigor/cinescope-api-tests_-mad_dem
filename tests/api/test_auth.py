"""Позитивные тесты для авторизации."""
import datetime
import allure
from pytest_check import check

from api.api_manager import ApiManager
from constants.roles import Roles
from models.base_models import RegisterUserResponse, TestUser


@allure.title("Тест регистрации пользователя с помощью Mock")
@allure.severity(allure.severity_level.MINOR)
@allure.label("qa_name", "Komin Igor")
def test_register_user_mock(api_manager: ApiManager, test_user: TestUser, mocker):
    """
    Тест регистрации с моком.
    Проверяет, что ответ соответствует замоканному значению.
    """
    with allure.step("Мокаем метод register_user в auth_api"):
        mock_response = RegisterUserResponse(
            id="mock-id-123",
            email="mock@email.com",
            fullName="Mock User",
            verified=True,
            banned=False,
            roles=[Roles.SUPER_ADMIN],
            createdAt=datetime.datetime.now().isoformat()
        )

        mocker.patch.object(
            api_manager.auth_api,
            'register_user',
            return_value=mock_response
        )

    with allure.step("Вызываем замоканный метод"):
        register_user_response = api_manager.auth_api.register_user(test_user)

    with allure.step("Проверяем, что ответ соответствует моку"):
        with allure.step("Проверка полей персонализации"):
            with check:
                check.equal(register_user_response.fullName, "Mock User", "НЕСОВПАДЕНИЕ fullName")
                check.equal(register_user_response.email, mock_response.email, "НЕСОВПАДЕНИЕ email")

        with allure.step("Проверка поля banned"):
            with check:
                check.equal(register_user_response.banned, mock_response.banned, "НЕСОВПАДЕНИЕ banned")
                check.equal(register_user_response.verified, mock_response.verified, "НЕСОВПАДЕНИЕ verified")

        with allure.step("Проверка ролей"):
            with check:
                check.equal(register_user_response.roles, mock_response.roles, "НЕСОВПАДЕНИЕ roles")