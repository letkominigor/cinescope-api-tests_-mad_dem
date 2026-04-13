"""Тесты удаления фильмов с валидацией в БД."""
import pytest
import allure
import random
from datetime import datetime, timezone
from db_models.movies import MovieDBModel
from constants.constants import STATUS_OK


@allure.feature("Movies API")
@allure.story("Удаление фильма с валидацией БД")
@allure.label("qa_name", "Komin Igor")
@allure.label("layer", "api+db")
class TestMovieDeleteWithDB:
    """Тесты удаления фильмов с проверкой в базе данных."""

    @allure.title("Удаление фильма супер-админом с валидацией в БД")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.api
    @pytest.mark.db
    @pytest.mark.positive
    def test_delete_movie_by_super_admin(self, super_admin, db_session):
        """Тест удаления фильма супер-админом с проверкой в БД."""
        # Arrange
        movie_id = random.randint(100000, 999999)

        with allure.step(f"Подготовка: создаём фильм с ID {movie_id} в БД"):
            existing_movie = db_session.query(MovieDBModel).filter(
                MovieDBModel.id == movie_id
            ).first()

            if not existing_movie:
                test_movie = MovieDBModel(
                    id=movie_id,
                    name=f"Test Movie for Deletion {random.randint(1000, 9999)}",
                    price=100.0,
                    description="Test description for deletion",
                    image_url="https://example.com/image.jpg",
                    location="MSK",
                    published=True,
                    rating=5.0,
                    genre_id="1",
                    created_at=datetime.now(timezone.utc)
                )
                db_session.add(test_movie)
                db_session.commit()

        try:
            # Act
            with allure.step("Проверяем, что фильм существует в БД"):
                movie_in_db = db_session.query(MovieDBModel).filter(
                    MovieDBModel.id == movie_id
                ).first()
                assert movie_in_db is not None, "Фильм должен существовать в БД"

            with allure.step("Удаляем фильм через API"):
                delete_response = super_admin.api.movies_api.delete_movie(movie_id=movie_id)
                assert delete_response.status_code == STATUS_OK, "Фильм должен успешно удалиться"

            # Assert
            with allure.step("Проверяем, что фильм удалён из БД"):
                movie_after_delete = db_session.query(MovieDBModel).filter(
                    MovieDBModel.id == movie_id
                ).first()
                assert movie_after_delete is None, "Фильм должен быть удалён из БД"

        finally:
            # Cleanup
            with allure.step("Очистка: удаляем тестовый фильм если остался"):
                remaining_movie = db_session.query(MovieDBModel).filter(
                    MovieDBModel.id == movie_id
                ).first()
                if remaining_movie:
                    db_session.delete(remaining_movie)
                    db_session.commit()