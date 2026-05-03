"""Фикстуры для тестов."""
import time
from typing import Generator
import allure
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


@allure.title("Задержка между повторными попытками")
@allure.description("Фикстура для добавления delay между ретраями")
@pytest.fixture
def delay_between_retries():
    time.sleep(2)
    yield


@allure.title("Базовые данные тестового пользователя")
@allure.description("Генерирует модель TestUser с рандомными данными")
@allure.feature("Auth")
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


@allure.title("Данные для создания пользователя")
@allure.description("Дополняет test_user полями verified и banned")
@allure.feature("Auth")
@pytest.fixture(scope="function")
def creation_user_data(test_user):
    updated_data = test_user.model_dump()
    updated_data.update({
        "verified": True,
        "banned": False
    })
    return updated_data


@allure.title("Зарегистрированный пользователь")
@allure.description("Регистрирует пользователя через API и возвращает модель с ID")
@allure.feature("Auth")
@allure.story("Регистрация")
@pytest.fixture(scope="function")
def registered_user(api_manager, test_user: TestUser) -> TestUser:
    response = api_manager.auth_api.register_user(user_data=test_user.model_dump())
    response_data = response.json()
    return test_user.model_copy(update={"id": response_data["id"]})


@allure.title("HTTP-сессия")
@allure.description("Создаёт и закрывает requests.Session")
@allure.feature("Infrastructure")
@pytest.fixture(scope="session")
def session():
    """Фикстура для создания HTTP-сессии."""
    http_session = requests.Session()
    yield http_session
    http_session.close()


@allure.title("Экземпляр ApiManager")
@allure.description("Инициализирует ApiManager с переданной сессией")
@allure.feature("Infrastructure")
@pytest.fixture(scope="function")
def api_manager(session):
    """Фикстура для создания экземпляра ApiManager."""
    return ApiManager(session)


@allure.title("Авторизация под админом")
@allure.description("Логинит админа и добавляет токен в заголовки сессии")
@allure.feature("Movies")
@allure.story("Авторизация")
@allure.severity(allure.severity_level.MINOR)
@pytest.fixture(scope="function")
def admin_session(api_manager):
    """Фикстура: авторизует сессию под админом для тестов фильмов."""
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

@allure.title("Созданный фильм")
@allure.description("Создаёт опубликованный фильм и возвращает (данные, api_manager)")
@allure.feature("Movies")
@allure.story("CRUD фильма")
@allure.severity(allure.severity_level.NORMAL)
@pytest.fixture(scope="function")
def created_movie_with_session(admin_session):
    """Фикстура: создаёт ОПУБЛИКОВАННЫЙ фильм и возвращает кортеж (данные, api_manager)."""
    movie_data = DataGenerator.generate_movie_data(published=True)

    create_response = admin_session.movies_api.create_movie(
        movie_data,
        expected_status=201
    )
    movie = create_response.json()

    yield movie, admin_session

    admin_session.movies_api.delete_movie(movie["id"], expected_status=200)


@allure.title("Опубликованный фильм")
@allure.description("Создаёт опубликованный фильм и удаляет после теста")
@allure.feature("Movies")
@allure.story("Фильтрация")
@allure.severity(allure.severity_level.NORMAL)
@pytest.fixture(scope="function")
def published_movie(admin_session):
    """
    Фикстура: создаёт опубликованный фильм и удаляет после теста.
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


@allure.title("Опубликованный фильм с сессией API")
@allure.description("Создаёт фильм и возвращает (данные, ТОТ ЖЕ api_manager)")
@allure.feature("Movies")
@pytest.fixture(scope="function")
def published_movie_with_session(admin_session):
    movie_data = DataGenerator.generate_movie_data(published=True)

    print(f"Создаем фильм с данными: {movie_data}")

    create_response = admin_session.movies_api.create_movie(
        movie_data,
        expected_status=201
    )
    movie = create_response.json()

    yield movie, admin_session

    admin_session.movies_api.delete_movie(movie["id"], expected_status=200)

@allure.title("Супер-админ пользователь")
@allure.description("Создаёт сессию и авторизует супер-админа")
@allure.feature("RBAC")
@allure.story("Роли пользователей")
@allure.severity(allure.severity_level.CRITICAL)
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


@allure.title("Обычный пользователь (USER)")
@allure.description("Создаёт пользователя с ролью USER через супер-админа")
@allure.feature("RBAC")
@allure.story("Роли пользователей")
@allure.severity(allure.severity_level.NORMAL)
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


@allure.title("Пользователь с ролью ADMIN")
@allure.description("Создаёт пользователя с ролью ADMIN через супер-админа")
@allure.feature("RBAC")
@allure.story("Роли пользователей")
@allure.severity(allure.severity_level.NORMAL)
@pytest.fixture
def admin_user(user_session, super_admin):
    """
    Фикстура пользователь с ролью ADMIN.
    Генерирует УНИКАЛЬНЫЕ данные каждый раз!
    """
    new_session = user_session()
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


@allure.title("Фабрика пользовательских сессий")
@allure.description("Создаёт изолированные сессии для разных пользователей")
@allure.feature("Infrastructure")
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


@allure.title("Данные для регистрации пользователя")
@allure.description("Конвертирует TestUser в JSON-формат для API")
@allure.feature("Auth")
@pytest.fixture
def registration_user_data(test_user: TestUser) -> dict:
    """Фикстура: данные для регистрации в JSON-формате"""
    return test_user.model_dump(mode='json', exclude_unset=True)


@allure.title("Сессия базы данных")
@allure.description("Предоставляет SQLAlchemy-сессию с авто-commit/rollback")
@allure.feature("Database")
@allure.story("Работа с БД")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    Фикстура для работы с БД (использует DBClient).
    """
    db_client = DBClient()
    with db_client.get_session() as session:
        yield session


