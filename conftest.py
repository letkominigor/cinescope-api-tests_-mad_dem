"""Фикстуры для тестов."""
import time
from typing import Generator

import pytest
import requests
from faker import Faker
from sqlalchemy.orm import Session
from api.api_manager import ApiManager
from constants.roles import Roles
from db_requester import DBClient
from entities.user import User
from models.base_models import TestUser
from resources.user_creds import SuperAdminCreds
from utils.data_generator import DataGenerator

faker = Faker()

@pytest.fixture #была добавлена в файл conftest.py
def delay_between_retries():
    time.sleep(2)
    yield

@pytest.fixture
def test_user() -> TestUser:
    """Фикстура: базовые данные пользователя как модель"""
    password = DataGenerator.generate_random_password()
    return TestUser(
        email=DataGenerator.generate_random_email(),
        fullName=DataGenerator.generate_random_name(),
        password=password,
        passwordRepeat=password,
        roles=[Roles.USER]
    )

@pytest.fixture(scope="function")
def creation_user_data(test_user):
    updated_data = test_user.model_dump()
    updated_data.update({
        "verified": True,
        "banned": False
    })
    return updated_data


@pytest.fixture(scope="function")
def registered_user(api_manager, test_user: TestUser) -> TestUser:
    response = api_manager.auth_api.register_user(user_data=test_user.model_dump())
    response_data = response.json()

    return test_user.model_copy(update={"id": response_data["id"]})

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
def common_user(user_session, super_admin):
    """Фикстура: обычный пользователь для тестов."""
    new_session = user_session()
    user_data = DataGenerator.generate_user_data(role="USER")

    common_user = User(
        user_data['email'],
        user_data['password'],
        [Roles.USER.value],
        new_session
    )

    create_response = super_admin.api.user_api.create_user(user_data)
    common_user.id = create_response.json()["id"]
    common_user.api.auth_api.authenticate(common_user.creds)

    yield common_user

    if hasattr(common_user, 'id') and common_user.id:
        try:
            super_admin.api.user_api.delete_user(common_user.id, expected_status=200)
        except:
            pass


@pytest.fixture
def admin_user(user_session, super_admin):
    """
    Фикстура пользователь с ролью ADMIN.
    Генерирует УНИКАЛЬНЫЕ данные каждый раз!
    """
    new_session = user_session()

    # Генерируем уникальные данные прямо здесь
    user_data = DataGenerator.generate_user_data(role="ADMIN")

    admin_user = User(
        user_data['email'],
        user_data['password'],
        [Roles.ADMIN.value],
        new_session
    )

    create_response = super_admin.api.user_api.create_user(user_data)
    admin_user.id = create_response.json()["id"]

    admin_user.api.auth_api.authenticate(admin_user.creds)

    yield admin_user

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

@pytest.fixture
def registration_user_data(test_user: TestUser) -> dict:
    """Фикстура: данные для регистрации в JSON-формате"""
    return test_user.model_dump(mode='json', exclude_unset=True)

@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    Фикстура для работы с БД (использует DBClient).
    """
    db_client = DBClient()
    with db_client.get_session() as session:
        yield session

