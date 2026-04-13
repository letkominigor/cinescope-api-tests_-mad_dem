"""Тесты жизненного цикла фильма с валидацией данных в БД."""
from db_requester import DBClient
from utils.data_generator import DataGenerator


class TestMovieLifecycle:
    """Тесты полного цикла фильма с проверкой БД."""

    def test_movie_crud_with_db_validation(self, admin_session):
        """Проверяет целостность данных между API и БД на всех этапах."""
        db = DBClient()

        movie_data = DataGenerator.generate_movie_data(
            name=f"Test Movie DB {DataGenerator.generate_random_email()}",
            location="MSK",
            published=True,
            genre_id=2,
            price=500
        )

        existing_movies = db.execute_query(
            "SELECT id FROM movies WHERE name = :name",
            {"name": movie_data["name"]}
        )
        assert len(existing_movies) == 0

        create_response = admin_session.movies_api.create_movie(movie_data)
        movie_id = create_response.json()["id"]

        try:
            assert db.movie_exists(movie_id)

            db_movie = db.get_movie_by_id(movie_id)
            assert db_movie["name"] == movie_data["name"]
            assert float(db_movie["price"]) == float(movie_data["price"])

        finally:
            admin_session.movies_api.delete_movie(movie_id, expected_status=200)

            assert not db.movie_exists(movie_id)