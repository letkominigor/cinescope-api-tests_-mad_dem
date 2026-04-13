"""Параметризованные тесты для фильтрации фильмов."""
import pytest
import allure
from api.api_manager import ApiManager
from utils.data_generator import DataGenerator
from constants.constants import STATUS_OK


@allure.feature("Movies API")
@allure.story("Фильтрация фильмов")
@allure.label("qa_name", "Komin Igor")
@allure.label("layer", "api")
class TestMovieFilters:
    """Тесты для проверки фильтров эндпоинта GET /movies"""

    @allure.title("Фильтрация фильмов по ценовому диапазону")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    @pytest.mark.positive
    @pytest.mark.parametrize(
        "filter_params, filter_name",
        [
            ({"minPrice": 1, "maxPrice": 500}, "price_1_to_500"),
            ({"minPrice": 500, "maxPrice": 1000}, "price_500_to_1000"),
            ({"minPrice": 1000, "maxPrice": 2000}, "price_1000_to_2000"),
        ],
        ids=["price_low", "price_medium", "price_high"]
    )
    def test_filter_by_price_range(
        self,
        api_manager: ApiManager,
        filter_params: dict,
        filter_name: str
    ):
        """Фильтрация по ценовому диапазону"""
        # Act
        with allure.step(f"Запрашиваем фильмы с фильтром {filter_name}"):
            response = api_manager.movies_api.get_movies_list(
                params=filter_params,
                expected_status=STATUS_OK
            )

        # Assert
        with allure.step("Проверяем, что список не пустой"):
            response_data = response.json()
            movies_list = response_data.get("movies", [])
            assert len(movies_list) > 0, f"Список фильмов с фильтром '{filter_name}' не должен быть пустым"

        with allure.step("Проверяем, что все фильмы в диапазоне цен"):
            for movie in movies_list:
                price = movie.get("price", 0)
                if "minPrice" in filter_params:
                    assert price >= filter_params["minPrice"]
                if "maxPrice" in filter_params:
                    assert price <= filter_params["maxPrice"]

    @allure.title("Фильтрация фильмов по жанру")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    @pytest.mark.positive
    @pytest.mark.parametrize(
        "genre_id, genre_name",
        [(1, "genre_1"), (2, "genre_2"), (3, "genre_3"), (4, "genre_4")],
        ids=["genre_1", "genre_2", "genre_3", "genre_4"]
    )
    def test_filter_by_genre_id(
        self,
        api_manager: ApiManager,
        genre_id: int,
        genre_name: str
    ):
        """Фильтрация по жанру"""
        # Act
        with allure.step(f"Запрашиваем фильмы с жанром {genre_name}"):
            response = api_manager.movies_api.get_movies_list(
                params={"genreId": genre_id},
                expected_status=STATUS_OK
            )

        # Assert
        with allure.step("Проверяем, что список не пустой"):
            response_data = response.json()
            movies_list = response_data.get("movies", [])
            assert len(movies_list) > 0, f"Список фильмов с жанром '{genre_name}' не должен быть пустым"

        with allure.step("Проверяем, что все фильмы имеют правильный жанр"):
            for movie in movies_list:
                assert movie.get("genreId") == genre_id

    @allure.title("Фильтрация по локации с созданием тестового фильма")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    @pytest.mark.positive
    def test_filter_by_location_with_created_film(self, admin_session: ApiManager):
        """Тест: фильтрация по локации с проверкой созданного фильма"""
        # Arrange
        unique_location = "MSK"

        with allure.step(f"Создаём тестовый фильм с локацией {unique_location}"):
            movie_data = DataGenerator.generate_movie_data(location=unique_location)
            create_response = admin_session.movies_api.create_movie(movie_data)
            movie_id = create_response.json()["id"]

        try:
            # Act
            with allure.step(f"Получаем фильм с ID {movie_id}"):
                response = admin_session.movies_api.get_movie_by_id(
                    movie_id,
                    expected_status=STATUS_OK
                )
                response_data = response.json()

            # Assert
            with allure.step("Проверяем, что локация совпадает"):
                assert response_data["location"] == unique_location, (
                    f"Фильм {movie_id} имеет локацию '{response_data['location']}', "
                    f"ожидалось '{unique_location}'"
                )

        finally:
            # Cleanup
            with allure.step("Удаляем тестовый фильм"):
                admin_session.movies_api.delete_movie(movie_id, expected_status=STATUS_OK)

    @allure.title("Комбинированная фильтрация фильмов")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.api
    @pytest.mark.positive
    def test_combined_filters(self, admin_session: ApiManager, api_manager):
        """Комбинация нескольких фильтров"""
        # Arrange
        filter_params = {
            "minPrice": 1,
            "maxPrice": 1000,
            "genreId": 3
        }

        # Act
        with allure.step("Запрашиваем фильмы с комбинированными фильтрами"):
            response = api_manager.movies_api.get_movies_list(
                params=filter_params,
                expected_status=STATUS_OK
            )

        # Assert
        with allure.step("Проверяем, что список не пустой"):
            response_data = response.json()
            movies_list = response_data.get("movies", [])
            assert len(movies_list) > 0, "Список фильмов с комбинированными фильтрами не должен быть пустым"

        with allure.step("Проверяем, что все фильмы соответствуют фильтрам"):
            for movie in movies_list:
                price = movie.get("price", 0)
                assert 1 <= price <= 1000, f"Цена {price} не в диапазоне [1, 1000]"
                assert movie.get("genreId") == 3, f"Жанр {movie.get('genreId')} != 3"