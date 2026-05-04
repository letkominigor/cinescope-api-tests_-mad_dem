"""Тесты отзывов к фильмам — УПРОЩЁННАЯ ВЕРСИЯ."""
import allure
import pytest
from playwright.sync_api import Page
from utils.data_generator import DataGenerator
from models.movie_page import MoviePage
from models.page_object_models import CinescopeLoginPage


@allure.feature("UI Tests")
@allure.story("Отзывы к фильмам")
@allure.label("qa_name", "Komin Igor")
@allure.label("layer", "ui")
class TestMovieReview:

    @allure.title("Успешное оставление отзыва под фильмом")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.ui
    @pytest.mark.positive
    def test_add_review_to_movie(self, page: Page, registered_user):
        """Позитивный тест: авторизованный пользователь оставляет отзыв."""
        movie_id = 45261
        random_name = DataGenerator.generate_random_name()
        random_int = DataGenerator.generate_random_int(1, 100)
        review_text = f"Отличный фильм! {random_name} #{random_int}"
        rating = 5

        # Авторизация
        with allure.step("Авторизация"):
            login_page = CinescopeLoginPage(page)
            login_page.open()
            login_page.login(registered_user.email, registered_user.password)
            login_page.assert_alert_was_pop_up("Вы вошли в аккаунт")

        # Переход на страницу фильма
        with allure.step(f"Переход на страницу фильма #{movie_id}"):
            movie_page = MoviePage(page, movie_id)
            movie_page.open()

        # Заполнение и отправка отзыва
        with allure.step(f"Установка рейтинга: {rating}"):
            movie_page.set_rating(rating)

        with allure.step(f"Ввод текста: '{review_text[:30]}...'"):
            movie_page.fill_review_text(review_text)

        with allure.step("Отправка отзыва"):
            movie_page.submit_review()

        # Минимальная проверка
        with allure.step("Проверка успешной отправки"):
            movie_page.assert_review_submitted()

        # Скриншот
        with allure.step("Скриншот"):
            allure.attach(
                page.screenshot(),
                name="Review submitted",
                attachment_type=allure.attachment_type.PNG
            )
