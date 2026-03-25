"""Фикстуры для тестов."""
import pytest
import requests
from faker import Faker

from api.api_manager import ApiManager
from constants.roles import Roles
from custom_requester.custom_requester import RequestError
from entities.user import User
from resources.user_creds import SuperAdminCreds
from utils.data_generator import DataGenerator

faker = Faker()


@pytest.fixture(scope="function")
def test_user():
    random_password = DataGenerator.generate_random_password()

    return {
        "email": DataGenerator.generate_random_email(),
        "fullName": DataGenerator.generate_random_name(),
        "password": random_password,
        "passwordRepeat": random_password,
        "roles": [Roles.USER.value]
    }


@pytest.fixture(scope="function")
def creation_user_data(test_user):
    """
    Фикстура: данные пользователя для создания (до регистрации).

    Добавляет поля verified и banned, которые обычно возвращает сервер
    после успешной регистрации.

    :param test_user: базовые данные пользователя
    :return: dict с полными данными пользователя
    """
    updated_data = test_user.copy()
    updated_data.update({
        "verified": True,
        "banned": False
    })
    return updated_data


@pytest.fixture(scope="function")
def registered_user(api_manager, test_user):
    """
    Фикстура для регистрации и получения данных пользователя.

    :param api_manager: ApiManager экземпляр
    :param test_user: данные для регистрации
    :return: dict с данными зарегистрированного пользователя
    """
    response = api_manager.auth_api.register_user(user_data=test_user)
    response_data = response.json()
    registered_user = test_user.copy()
    registered_user["id"] = response_data["id"]
    return registered_user


@pytest.fixture(scope="session")
def session():
    """Фикстура для создания HTTP-сессии."""
    http_session = requests.Session()
    yield http_session
    http_session.close()


@pytest.fixture(scope="session")
def api_manager(session):
    """Фикстура для создания экземпляра ApiManager."""
    return ApiManager(session)


@pytest.fixture(scope="function")
def admin_session(api_manager):
    """
    Фикстура: авторизует сессию под админом для тестов фильмов.

    :param api_manager: ApiManager экземпляр
    :return: api_manager с активным токеном админа
    """
    admin_creds = {
        "email": "api1@gmail.com",
        "password": "asdqwe123Q"
    }

    response = api_manager.auth_api.login_user(
        login_data=admin_creds,
        expected_status=200
    )

    token = response.json()["accessToken"]
    api_manager.auth_api._update_session_headers(
        authorization=f"Bearer {token}"
    )

    return api_manager


@pytest.fixture(scope="function")
def created_movie(admin_session):
    """
    Фикстура: создаёт фильм через API и удаляет его после теста.

    :param admin_session: ApiManager с авторизацией под админом
    :return: dict с данными созданного фильма (id, name, location, и т.д.)

    Пример использования:
        def test_update_movie(self, created_movie, admin_session):
            movie_id = created_movie["id"]
    """
    movie_data = DataGenerator.generate_movie_data()

    create_response = admin_session.movies_api.create_movie(
        movie_data,
        expected_status=201
    )
    movie_data_response = create_response.json()

    yield movie_data_response

    admin_session.movies_api.delete_movie(
        movie_data_response["id"],
        expected_status=200
    )


@pytest.fixture(scope="function")
def published_movie(admin_session):
    """
    Фикстура: создаёт опубликованный фильм и удаляет после теста.

    :param admin_session: ApiManager с авторизацией под админом
    :return: dict с данными созданного фильма
    """
    movie_data = DataGenerator.generate_movie_data(published=True)
    create_response = admin_session.movies_api.create_movie(
        movie_data,
        expected_status=201
    )
    movie_data_response = create_response.json()

    yield movie_data_response

    admin_session.movies_api.delete_movie(
        movie_data_response["id"],
        expected_status=200
    )


@pytest.fixture
def super_admin(user_session):
    """Фикстура: супер-админ для тестов."""
    new_session = user_session()
    super_admin = User(
        SuperAdminCreds.USERNAME,
        SuperAdminCreds.PASSWORD,
        [Roles.SUPER_ADMIN.value],
        new_session
    )

    super_admin.api.auth_api.authenticate(super_admin.creds)
    return super_admin


@pytest.fixture
def common_user(user_session, super_admin, creation_user_data):
    """Фикстура: обычный пользователь для тестов."""
    new_session = user_session()

    #  Пытаемся создать пользователя, но игнорируем 409 (уже существует)
    try:
        create_response = super_admin.api.user_api.create_user(creation_user_data)
        user_id = create_response.json()["id"]
    except RequestError as e:
        # Если ошибка НЕ 409 — пробрасываем дальше
        if e.response.status_code != 409:
            raise
        # Если 409 — пользователь уже есть, пропускаем создание
        user_id = None

    common_user = User(
        creation_user_data['email'],
        creation_user_data['password'],
        [Roles.USER.value],
        new_session
    )

    # Если у нас есть ID, сохраняем его для очистки
    if user_id:
        common_user.id = user_id

    common_user.api.auth_api.authenticate(common_user.creds)

    yield common_user

    # ✅ Очистка: удаляем только если id известен
    if hasattr(common_user, 'id') and common_user.id:
        try:
            super_admin.api.user_api.delete_user(common_user.id, expected_status=200)
        except:
            pass  # Игнорируем ошибки при удалении


@pytest.fixture
def admin_user(user_session, super_admin, creation_user_data):
    """Фикстура: пользователь с ролью ADMIN."""
    new_session = user_session()

    # Создаём и получаем ID, игнорируя 409
    try:
        create_response = super_admin.api.user_api.create_user(creation_user_data)
        user_id = create_response.json()["id"]
    except RequestError as e:
        if e.response.status_code != 409:
            raise
        user_id = None

    admin_user = User(
        creation_user_data['email'],
        creation_user_data['password'],
        [Roles.ADMIN.value],
        new_session
    )

    if user_id:
        admin_user.id = user_id

    admin_user.api.auth_api.authenticate(admin_user.creds)

    yield admin_user

    # Очистка
    if hasattr(admin_user, 'id') and admin_user.id:
        try:
            super_admin.api.user_api.delete_user(admin_user.id, expected_status=200)
        except:
            pass

@pytest.fixture
def user_session():
    """Фикстура для создания изолированных сессий пользователей."""
    user_pool = []

    def _create_user_session():
        session = requests.Session()
        user_session = ApiManager(session)
        user_pool.append(user_session)
        return user_session

    yield _create_user_session

    for user in user_pool:
        user.close_session()