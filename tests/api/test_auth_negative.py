import pytest
from api.api_manager import ApiManager
from custom_requester.custom_requester import RequestError


class TestAuthNegative:
    """Негативные тесты для авторизации."""

    def test_login_with_wrong_password(self, api_manager: ApiManager, registered_user):
        """
        Тест 1: Авторизация с неверным паролем.
        Ожидается: 401 или 500 + сообщение об ошибке
        """
        login_data = {
            "email": registered_user.email,
            "password": "WrongPassword123!"
        }

        with pytest.raises(RequestError) as exc_info:
            api_manager.auth_api.login_user(login_data=login_data, expected_status=200)

        assert exc_info.value.response.status_code in [401, 500], \
            f"Ожидали 401/500, получили {exc_info.value.response.status_code}"

        response_data = exc_info.value.response.json()
        assert "message" in response_data or "error" in response_data, \
            "В ответе должно быть сообщение об ошибке"


    def test_login_with_nonexistent_email(self, api_manager: ApiManager):
        """
        Тест 2: Авторизация с несуществующим email.
        Ожидается: 401 + сообщение об ошибке
        """
        login_data = {
            "email": "nonexistent_user_abc123@test.com",  # Такого пользователя нет
            "password": "SomeValidPass123!"
        }

        with pytest.raises(RequestError) as exc_info:
            api_manager.auth_api.login_user(login_data=login_data, expected_status=200)

        assert exc_info.value.response.status_code in [401, 404, 500], \
            f"Ожидали 401/404/500, получили {exc_info.value.response.status_code}"

        response_data = exc_info.value.response.json()
        assert "message" in response_data or "error" in response_data, \
            "В ответе должно быть сообщение об ошибке"


    def test_login_with_empty_body(self, api_manager: ApiManager):
        """
        Тест 3: Авторизация с пустым телом запроса.
        Ожидается: 400 или 500 + сообщение об ошибке
        """
        login_data = {}

        with pytest.raises(RequestError) as exc_info:
            api_manager.auth_api.login_user(login_data=login_data, expected_status=200)

        assert exc_info.value.response.status_code in [400, 401, 500], \
            f"Ожидали 400/401/500, получили {exc_info.value.response.status_code}"

        response_data = exc_info.value.response.json()
        assert "message" in response_data or "error" in response_data, \
            "В ответе должно быть сообщение об ошибке"


    def test_login_with_empty_email(self, api_manager: ApiManager, registered_user):
        """Тест: авторизация с пустым email."""
        login_data = {
            "email": "",
            "password": registered_user.password
        }

        with pytest.raises(RequestError) as exc_info:
            api_manager.auth_api.login_user(login_data=login_data, expected_status=200)

        assert exc_info.value.response.status_code in [400, 401, 500]


    def test_login_with_empty_password(self, api_manager: ApiManager, registered_user):
        """Тест: авторизация с пустым паролем."""
        login_data = {
            "email": registered_user.email,
            "password": ""
        }

        with pytest.raises(RequestError) as exc_info:
            api_manager.auth_api.login_user(login_data=login_data, expected_status=200)

        assert exc_info.value.response.status_code in [400, 401, 500]