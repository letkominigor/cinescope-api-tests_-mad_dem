import datetime
import random
import string
from uuid import uuid4

from faker import Faker

faker = Faker()


class DataGenerator:
    """Генерация тестовых данных."""

    @staticmethod
    def generate_random_int(min_value: int = 0, max_value: int = 99999) -> int:
        return random.randint(min_value, max_value)

    @staticmethod
    def generate_random_email():
        """Генерация случайного email."""
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"kek{random_string}@gmail.com"

    @staticmethod
    def generate_random_name():
        """Генерация случайного имени."""
        return f"{faker.first_name()} {faker.last_name()}"


    @staticmethod
    def generate_random_password(length=12):
        """
        Генерирует случайный пароль, соответствующий требованиям валидации:
        - хотя бы одна строчная буква
        - хотя бы одна заглавная буква
        - хотя бы одна цифра
        - хотя бы один спецсимвол
        """
        import string
        import random

        password_chars = [
            random.choice(string.ascii_lowercase),
            random.choice(string.ascii_uppercase),
            random.choice(string.digits),
            random.choice("?@#$%^&*|:")
        ]

        # Все допустимые символы для заполнения
        all_chars = string.ascii_letters + string.digits + "?@#$%^&*|:"

        password_chars += [random.choice(all_chars) for _ in range(length - 4)]

        # Перемешиваем, чтобы обязательные символы не были в начале
        random.shuffle(password_chars)

        return ''.join(password_chars)

    """@staticmethod
    def generate_user_data(role="USER"):
        password = DataGenerator.generate_random_password()
        return {
            "email": DataGenerator.generate_random_email(),
            "fullName": DataGenerator.generate_random_name(),
            "password": password,
            "passwordRepeat": password,
            "roles": [role],
            "verified": True,
            "banned": False
        }"""

    @staticmethod
    def generate_user_data(role: str = "USER", verified: bool = True, banned: bool = False) -> dict:
        """
        Генерирует данные пользователя для отправки в API.

        :param role: Роль пользователя
        :param verified: Статус верификации (по умолчанию True)
        :param banned: Статус бана (по умолчанию False)
        :return: dict с данными
        """
        password = DataGenerator.generate_random_password()

        return {
            "email": DataGenerator.generate_random_email(),
            "fullName": DataGenerator.generate_random_name(),
            "password": password,
            "passwordRepeat": password,
            "roles": [role],
            "verified": verified,
            "banned": banned,
        }

    @staticmethod
    def generate_user_data_for_db(role: str = "USER") -> dict:
        """
        Генерирует данные пользователя для прямой вставки в БД (через SQLAlchemy).

        :param role: Роль пользователя
        :return: dict с данными в формате БД (snake_case)
        """
        password = DataGenerator.generate_random_password()
        now = datetime.datetime.now()

        return {
            "id": str(uuid4()),
            "email": DataGenerator.generate_random_email(),
            "full_name": DataGenerator.generate_random_name(),
            "password": password,
            "created_at": now,
            "updated_at": now,
            "verified": False,
            "banned": False,
            "roles": role,
        }

    @staticmethod
    def generate_movie_data(name=None, location=None, published=None, genre_id=None, price=None):
        """
        Генерация валидных данных для фильма.

        :param name: Название фильма
        :param location: Локация (MSK или SPB)
        :param published: Статус публикации
        :param genre_id: Жанр (1-4)
        :param price: Цена фильма
        """
        return {
            "name": name or f"Movie {faker.word().title()} {random.randint(1000, 9999)}",
            "price": price if price is not None else random.randint(100, 2000),
            "description": faker.sentence(nb_words=10),
            "imageUrl": f"https://picsum.photos/seed/{random.randint(1, 9999)}/400/600",
            "location": location or random.choice(["MSK", "SPB"]),
            "published": published if published is not None else random.choice([True, False]),
            "genreId": genre_id if genre_id is not None else random.randint(1, 4)
        }

    @staticmethod
    def generate_invalid_movie_data(invalid_field):
        """
        Генерация данных с одним невалидным полем.

        :param invalid_field: Название поля для невалидного значения
        :return: dict с невалидными данными
        """
        valid_data = DataGenerator.generate_movie_data()

        invalid_values = {
            "name": "",
            "price": "not_a_number",
            "location": "GOTHAM_CITY",
            "genreId": 99999,
            "rating": 15,
            "published": "stroka",
        }

        if invalid_field in invalid_values:
            valid_data[invalid_field] = invalid_values[invalid_field]

        return valid_data