"""Хелперы для работы с БД в тестах."""
from db_requester import DBClient
from db_models.user import UserDBModel
from db_models.movies import MovieDBModel


class DBHelper:
    """Класс с методами для работы с БД в тестах"""

    def __init__(self, db_client: DBClient = None):
        """
        Инициализация хелпера.

        :param db_client: Экземпляр DBClient (создаётся автоматически если None)
        """
        self.db_client = db_client or DBClient()

    def create_test_user(self, user_data: dict) -> UserDBModel:
        """Создает тестового пользователя"""
        with self.db_client.get_session() as session:
            user = UserDBModel(**user_data)
            session.add(user)
            return user

    def get_user_by_id(self, user_id: str):
        """Получает пользователя по ID"""
        with self.db_client.get_session() as session:
            return session.query(UserDBModel).filter(UserDBModel.id == user_id).first()

    def get_user_by_email(self, email: str):
        """Получает пользователя по email"""
        with self.db_client.get_session() as session:
            return session.query(UserDBModel).filter(UserDBModel.email == email).first()

    def get_movie_by_name(self, name: str):
        """Получает фильм по названию"""
        with self.db_client.get_session() as session:
            return session.query(MovieDBModel).filter(MovieDBModel.name == name).first()

    def user_exists_by_email(self, email: str) -> bool:
        """Проверяет существование пользователя по email"""
        with self.db_client.get_session() as session:
            count = session.query(UserDBModel).filter(UserDBModel.email == email).count()
            return count > 0

    def delete_user(self, user: UserDBModel):
        """Удаляет пользователя"""
        with self.db_client.get_session() as session:
            session.delete(user)

    def cleanup_test_data(self, objects_to_delete: list):
        """Очищает тестовые данные"""
        with self.db_client.get_session() as session:
            for obj in objects_to_delete:
                if obj:
                    session.delete(obj)

