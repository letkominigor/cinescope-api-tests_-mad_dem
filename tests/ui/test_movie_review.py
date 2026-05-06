"""Тесты отзывов к фильмам."""
import allure
import pytest
from playwright.sync_api import Page

from tests.ui.pages.login_page import CinescopeLoginPage
from utils.data_generator import DataGenerator
from tests.ui.pages.movie_page import MoviePage



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
    @allure.title("Успешное оставление отзыва под фильмом")
    def test_add_review_to_movie(self, page: Page, registered_user, available_movie_id):
        movie_id = available_movie_id

        with allure.step("Авторизация"):
            login_page = CinescopeLoginPage(page)
            login_page.open()
            login_page.login(registered_user.email, registered_user.password)
            login_page.assert_alert_was_pop_up("Вы вошли в аккаунт")

        with allure.step(f"Переход на страницу фильма #{movie_id}"):
            movie_page = MoviePage(page, movie_id)
            movie_page.open()

        with allure.step("Установка рейтинга: 5"):
            movie_page.set_rating(5)

        review_text = f"Отличный фильм! {DataGenerator.generate_random_name()}"

        with allure.step("Ввод текста: '{review_text[:30]}...'"):
            movie_page.fill_review_text(review_text)

        with allure.step("Отправка отзыва"):
            movie_page.submit_review()

        with allure.step("Проверка успешной отправки"):
            movie_page.assert_review_submitted(expected_text=review_text)

        with allure.step("Скриншот"):
            allure.attach(page.screenshot(), name="Review", attachment_type=allure.attachment_type.PNG)
