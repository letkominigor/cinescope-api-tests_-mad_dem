import random
import string
from faker import Faker

faker = Faker()


class DataGenerator:
    """Генерация тестовых данных."""

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
    def generate_random_password():
        """
        Генерация пароля, соответствующего требованиям:
        - Минимум 1 буква.
        - Минимум 1 цифра.
        - Допустимые символы.
        - Длина от 8 до 20 символов.
        """
        letters = random.choice(string.ascii_letters)
        digits = random.choice(string.digits)

        special_chars = "?@#$%^&*|:"
        all_chars = string.ascii_letters + string.digits + special_chars
        remaining_length = random.randint(6, 18)
        remaining_chars = ''.join(random.choices(all_chars, k=remaining_length))

        password = list(letters + digits + remaining_chars)
        random.shuffle(password)

        return ''.join(password)

    @staticmethod
    def generate_movie_data(name=None, location=None, published=None):
        """
        Генерация валидных данных для фильма.

        :param name: Название фильма (опционально)
        :param location: Локация показа (MSK или SPB)
        :param published: Статус публикации (True/False)
        :return: dict с данными фильма
        """
        return {
            "name": name or f"Movie {faker.word().title()} {random.randint(1000, 9999)}",
            "price": random.randint(100, 5000),
            "description": faker.sentence(nb_words=10),
            "imageUrl": f"https://picsum.photos/seed/{random.randint(1, 9999)}/400/600",
            "location": location or random.choice(["MSK", "SPB"]),
            "published": published if published is not None else random.choice([True, False]),
            "genreId": random.randint(1, 4),
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