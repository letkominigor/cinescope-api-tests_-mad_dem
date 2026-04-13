"""Клиент для работы с PostgreSQL базой данных."""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from contextlib import contextmanager
from resources.db_creds import get_movies_db_creds


class DBClient:
    """Клиент для работы с БД через SQLAlchemy."""

    def __init__(self):
        """Инициализация клиента БД."""
        creds = get_movies_db_creds()

        # Обработка порта
        port = creds.PORT if creds.PORT and creds.PORT != 'None' else 5432

        DATABASE_URL = (
            f"postgresql+psycopg2://{creds.USERNAME}:{creds.PASSWORD}"
            f"@{creds.HOST}:{port}/{creds.DATABASE_NAME}"
        )

        self.engine = create_engine(
            DATABASE_URL,
            echo=False,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10
        )

        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.db_session_factory = scoped_session(SessionLocal)

    @contextmanager
    def get_session(self):
        """Контекстный менеджер для работы с сессией."""
        session = self.db_session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
            self.db_session_factory.remove()

    @contextmanager
    def get_connection(self):
        """Контекстный менеджер для прямого подключения (без ORM)."""
        conn = self.engine.connect()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def execute_query(self, query: str, params: dict = None) -> list:
        """Выполняет SELECT-запрос."""
        with self.get_connection() as conn:
            result = conn.execute(text(query), params or {})
            return result.fetchall()

    def movie_exists(self, movie_id: str) -> bool:
        """Проверяет существование фильма по ID."""
        with self.get_connection() as conn:
            result = conn.execute(
                text("SELECT EXISTS(SELECT 1 FROM movies WHERE id = :movie_id)"),
                {"movie_id": movie_id}
            ).scalar()
            return bool(result)

    def get_movie_by_id(self, movie_id: str):
        """Получает фильм по ID (возвращает RowMapping)."""
        with self.get_connection() as conn:
            result = conn.execute(
                text("SELECT * FROM movies WHERE id = :movie_id"),
                {"movie_id": movie_id}
            ).fetchone()
            return result._mapping if result else None

    def get_movies_count(self) -> int:
        """Возвращает количество фильмов."""
        with self.get_connection() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM movies")).fetchone()
            return result[0] if result else 0

    def delete_movie(self, movie_id: str) -> bool:
        """Удаляет фильм по ID (ORM)."""
        with self.get_session() as session:
            from db_models.movies import MovieDBModel
            movie = session.query(MovieDBModel).filter(
                MovieDBModel.id == movie_id
            ).first()

            if movie:
                session.delete(movie)
                return True
            return False

    def delete_movie_by_id(self, movie_id: str) -> int:
        """Удаляет фильм по ID (raw SQL)."""
        with self.get_connection() as conn:
            result = conn.execute(
                text("DELETE FROM movies WHERE id = :movie_id"),
                {"movie_id": movie_id}
            )
            return result.rowcount

    def get_server_info(self) -> dict:
        """Получает информацию о сервере."""
        with self.get_connection() as conn:
            result = conn.execute(text("""
                SELECT version() as version, current_database() as database
            """)).fetchone()
            return {'version': result[0], 'database': result[1]}

    # Методы для аккаунтов (тест транзакций)

    def create_account(self, user: str, balance: float) -> dict:
        """Создаёт аккаунт и возвращает данные как dict (чтобы избежать DetachedInstanceError)."""
        with self.get_session() as session:
            from db_models.account import AccountTransactionTemplate
            account = AccountTransactionTemplate(user=user, balance=balance)
            session.add(account)
            return {'user': user, 'balance': balance}

    def get_account_balance(self, user: str) -> float | None:
        """Получает баланс аккаунта по имени пользователя."""
        with self.get_session() as session:
            from db_models.account import AccountTransactionTemplate
            result = session.query(AccountTransactionTemplate.balance).filter(
                AccountTransactionTemplate.user == user
            ).first()
            return result[0] if result else None

    def delete_account(self, user: str) -> bool:
        """Удаляет аккаунт по имени пользователя."""
        with self.get_session() as session:
            from db_models.account import AccountTransactionTemplate
            account = session.query(AccountTransactionTemplate).filter_by(user=user).first()
            if account:
                session.delete(account)
                return True
            return False


#  Функции для обратной совместимости (если нужны)
_db_client_instance = None


def get_db_client() -> DBClient:
    """Возвращает singleton-экземпляр DBClient."""
    global _db_client_instance
    if _db_client_instance is None:
        _db_client_instance = DBClient()
    return _db_client_instance


def get_db_session():
    """Возвращает сессию БД (Session объект)."""
    return get_db_client().db_session_factory()


def close_db_session(session):
    """Корректное закрытие сессии."""
    try:
        session.close()
    finally:
        get_db_client().db_session_factory.remove()