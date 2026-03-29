"""Параметризованные тесты для фильтрации фильмов."""
import pytest
from api.api_manager import ApiManager
from utils.data_generator import DataGenerator


class TestMovieFilters:
    """Тесты для проверки фильтров эндпоинта GET /movies"""

    @pytest.mark.parametrize(
        "filter_params, filter_name",
        [
            ({"minPrice": 1, "maxPrice": 500}, "price_1_to_500"),
            ({"minPrice": 500, "maxPrice": 1000}, "price_500_to_1000"),
            ({"minPrice": 1000, "maxPrice": 2000}, "price_1000_to_2000"),
        ],
        ids=["price_low", "price_medium", "price_high"]
    )
    def test_filter_by_price_range(self,api_manager: ApiManager,filter_params: dict,filter_name: str):
        """
        Фильтрация по ценовому диапазону
        """
        response = api_manager.movies_api.get_movies_list(
            params=filter_params,
            expected_status=200
        )
        response_data = response.json()
        movies_list = response_data.get("movies", [])

        assert len(movies_list) > 0, (
            f"Список фильмов с фильтром '{filter_name}' не должен быть пустым"
        )

        for movie in movies_list:
            price = movie.get("price", 0)

            if "minPrice" in filter_params:
                assert price >= filter_params["minPrice"]

            if "maxPrice" in filter_params:
                assert price <= filter_params["maxPrice"]

    @pytest.mark.parametrize(
        "genre_id, genre_name",
        [(1, "genre_1"),(2, "genre_2"),(3, "genre_3"),(4, "genre_4"),],
        ids=["genre_1", "genre_2", "genre_3", "genre_4"]
    )
    def test_filter_by_genre_id(self,api_manager: ApiManager,genre_id: int,genre_name: str):
        """
        Фильтрация по жанру
        """
        response = api_manager.movies_api.get_movies_list(
            params={"genreId": genre_id},
            expected_status=200
        )
        response_data = response.json()
        movies_list = response_data.get("movies", [])

        assert len(movies_list) > 0, (
            f"Список фильмов с жанром '{genre_name}' не должен быть пустым"
        )

        for movie in movies_list:
            assert movie.get("genreId") == genre_id

    def test_filter_by_location_with_created_film(self, admin_session: ApiManager):
        """
        Тест: фильтрация по локации.
        Проверяем, что созданный фильм существует и имеет правильную локацию.
        """
        unique_location = "MSK"

        movie_data = DataGenerator.generate_movie_data(location=unique_location)
        create_response = admin_session.movies_api.create_movie(movie_data)
        movie_id = create_response.json()["id"]

        try:
            response = admin_session.movies_api.get_movie_by_id(
                movie_id,
                expected_status=200
            )
            response_data = response.json()

            assert response_data["location"] == unique_location, (
                f"Фильм {movie_id} имеет локацию '{response_data['location']}', "
                f"ожидалось '{unique_location}'"
            )

        finally:
            admin_session.movies_api.delete_movie(movie_id, expected_status=200)

    def test_combined_filters(self, admin_session: ApiManager, api_manager):
        """
        Комбинация нескольких фильтров
        """
        filter_params = {
            "minPrice": 1,
            "maxPrice": 1000,
            "genreId": 3
        }

        response = api_manager.movies_api.get_movies_list(
            params=filter_params,
            expected_status=200
        )
        response_data = response.json()
        movies_list = response_data.get("movies", [])

        assert len(movies_list) > 0, (
            "Список фильмов с комбинированными фильтрами не должен быть пустым"
        )

        for movie in movies_list:
            price = movie.get("price", 0)
            assert 1 <= price <= 1000
            assert movie.get("genreId") == 3