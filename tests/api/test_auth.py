
from api.api_manager import ApiManager
from models.base_models import TestUser, RegisterUserResponse


class TestAuthAPI:

    def test_register_user(self, api_manager: ApiManager, registration_user_data):
        response = api_manager.auth_api.register_user(user_data=registration_user_data)
        register_user_response = RegisterUserResponse(**response.json())
        assert register_user_response.email == registration_user_data["email"], "Email не совпадает"

    def test_register_and_login_user(self, api_manager: ApiManager, registered_user: TestUser):
        """Тест регистрации + авторизации"""

        login_data = {
            "email": registered_user.email,
            "password": registered_user.password
        }

        response = api_manager.auth_api.login_user(login_data)
        response_data = response.json()

        assert "accessToken" in response_data
        assert response_data["user"]["email"] == registered_user.email