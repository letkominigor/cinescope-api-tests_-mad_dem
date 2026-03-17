import pytest
import requests
from faker import Faker
from api.api_manager import ApiManager
from utils.data_generator import DataGenerator

faker = Faker()

@pytest.fixture(scope="function")
def test_user():
    """
    Генерация случайного пользователя для тестов.
    """
    random_email = DataGenerator.generate_random_email()
    random_name = DataGenerator.generate_random_name()
    random_password = DataGenerator.generate_random_password()

    return {
        "email": random_email,
        "fullName": random_name,
        "password": random_password,
        "passwordRepeat": random_password,
        "roles": ["USER"]
    }

@pytest.fixture(scope="function")
def registered_user(api_manager, test_user):
    """
    Фикстура для регистрации и получения данных зарегистрированного пользователя.
    """
    response = api_manager.auth_api.register_user(user_data=test_user) # тут посмотреть
    response_data = response.json()
    registered_user = test_user.copy()
    registered_user["id"] = response_data["id"]
    return registered_user

# Фикстура, которая будет создавать  сессию
@pytest.fixture(scope="session")
def session():
    """
    Фикстура для создания HTTP-сессии.
    """
    http_session = requests.Session()
    yield http_session
    http_session.close()

@pytest.fixture(scope="session")
def api_manager(session):
    """
    Фикстура для создания экземпляра ApiManager.
    """
    return ApiManager(session)


# conftest.py — добавь в конец файла

@pytest.fixture(scope="function")
def admin_session(api_manager):
    """
    Фикстура: авторизует сессию под админом для тестов фильмов.

    Возвращает api_manager с активным токеном админа.
    """
    admin_creds = {
        "email": "api1@gmail.com",
        "password": "asdqwe123Q"
    }

    # Логин
    response = api_manager.auth_api.login_user(
        login_data=admin_creds,
        expected_status=200
    )

    # Получаем и добавляем токен
    token = response.json()["accessToken"]
    api_manager.auth_api._update_session_headers(
        authorization=f"Bearer {token}"
    )

    return api_manager
"""registered_user зависит от:
- api_manager (для регистрации через API)
- test_user (данные для регистрации)
"""
