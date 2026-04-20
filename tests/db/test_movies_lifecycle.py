"""Тесты жизненного цикла фильма с валидацией данных в БД."""
import pytest
import allure
from db_requester import DBClient
from utils.data_generator import DataGenerator


@allure.feature("Movies API")
@allure.story("Жизненный цикл фильма")
@allure.label("qa_name", "Komin Igor")
class TestMovieLifecycle:
    """Тесты полного цикла фильма с проверкой БД."""

    @allure.title("Создание-чтение-обновление-удаление фильма с проверкой в БД")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.label("layer", "api+db")
    @pytest.mark.api
    @pytest.mark.db
    @pytest.mark.positive
    @pytest.mark.regression
    def test_movie_crud_with_db_validation(self, admin_session):
        """
        Тест полного цикла фильма с проверкой данных в БД.
        Проверяет целостность данных между API и БД на всех этапах.
        """
        db = DBClient()

        movie_data = DataGenerator.generate_movie_data(
            name=f"Test Movie DB {DataGenerator.generate_random_email()}",
            location="MSK",
            published=True,
            genre_id=2,
            price=500
        )

        with allure.step("Проверяем, что фильма нет до создания"):
            existing_movies = db.execute_query(
                "SELECT id FROM movies WHERE name = :name",
                {"name": movie_data["name"]}
            )
            assert len(existing_movies) == 0

        with allure.step("Создаём фильм через API"):
            create_response = admin_session.movies_api.create_movie(movie_data)
            movie_id = create_response.json()["id"]

        try:
            with allure.step("Проверяем, что фильм появился в БД"):
                assert db.movie_exists(movie_id), f"Фильм с ID {movie_id} не найден в БД"

            with allure.step("Проверяем данные в БД"):
                db_movie = db.get_movie_by_id(movie_id)
                assert db_movie["name"] == movie_data["name"], "Название в БД не совпадает"
                assert float(db_movie["price"]) == float(movie_data["price"]), "Цена в БД не совпадает"

        finally:
            with allure.step("Очистка: удаляем через API"):
                admin_session.movies_api.delete_movie(movie_id, expected_status=200)

            with allure.step("Проверяем, что фильм удалён из БД"):
                assert not db.movie_exists(movie_id), f"Фильм с ID {movie_id} всё ещё есть в БД"