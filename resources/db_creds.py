
import os
from dotenv import load_dotenv
from typing import NamedTuple

load_dotenv()


class MoviesDbCreds(NamedTuple):
    """Креды для подключения к БД фильмов"""
    HOST: str
    PORT: int
    DATABASE_NAME: str
    USERNAME: str
    PASSWORD: str

    @classmethod
    def load(cls) -> "MoviesDbCreds":
        """Загружает креды из .env с валидацией"""
        host = os.getenv("DB_HOST")
        port = os.getenv("DB_PORT")
        database = os.getenv("DB_NAME")
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")

        # Проверка на отсутствующие переменные
        missing = []
        if not host or host == "None": missing.append("DB_HOST")
        if not port or port == "None": missing.append("DB_PORT")
        if not database or database == "None": missing.append("DB_NAME")
        if not user or user == "None": missing.append("DB_USER")
        if not password or password == "None": missing.append("DB_PASSWORD")

        if missing:
            raise ValueError(f"Отсутствуют переменные в .env: {missing}")

        return cls(
            HOST=host,
            PORT=int(port),
            DATABASE_NAME=database,
            USERNAME=user,
            PASSWORD=password,
        )


# Глобальная функция для получения кредов
def get_movies_db_creds() -> MoviesDbCreds:
    return MoviesDbCreds.load()