import random
import string
from faker import Faker

faker = Faker()


class DataGenerator:

    @staticmethod
    def generate_random_email():
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"kek{random_string}@gmail.com"


    @staticmethod
    def generate_random_name():
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
        # Гарантируем наличие хотя бы одной буквы и одной цифры
        letters = random.choice(string.ascii_letters)  # Одна буква
        digits = random.choice(string.digits)  # Одна цифра

        # Дополняем пароль случайными символами из допустимого набора
        special_chars = "?@#$%^&*|:"
        all_chars = string.ascii_letters + string.digits + special_chars
        remaining_length = random.randint(6, 18)  # Остальная длина пароля
        remaining_chars = ''.join(random.choices(all_chars, k=remaining_length))

        # Перемешиваем пароль для рандомизации
        password = list(letters + digits + remaining_chars)
        random.shuffle(password)

        return ''.join(password)

    @staticmethod
    def generate_movie_data(name=None, genre_name=None, location=None):
        """Генерация валидных данных для фильма."""
        return {
            "name": name or f"Movie {faker.word().title()} {random.randint(1000, 9999)}",
            "price": random.randint(100, 5000),
            "description": faker.sentence(nb_words=10),
            "imageUrl": f"https://picsum.photos/seed/{random.randint(1, 9999)}/400/600",

            "location": location or random.choice(["MSK", "SPB"]),
            "published": random.choice([True, False]),
            "genreId": random.randint(1, 10),
            "rating": random.randint(1, 10)
        }

    @staticmethod
    def generate_invalid_movie_data(invalid_field):
        """Генерация данных с одним невалидным полем."""
        valid_data = DataGenerator.generate_movie_data()

        # Одно невалидное значение на поле — достаточно для тестов
        invalid_values = {
            "name": "",  # Пустая строка
            "price": "not_a_number",  # Строка вместо числа
            "location": "GOTHAM_CITY",  # Несуществующая локация
            "genreId": 99999,  # Несуществующий жанр
            "rating": 15,  # Рейтинг > 10
            "published": "stroka",  # Строка вместо boolean
        }

        if invalid_field in invalid_values:
            valid_data[invalid_field] = invalid_values[invalid_field]

        return valid_data