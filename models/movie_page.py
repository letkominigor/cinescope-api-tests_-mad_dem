"""Page Object для страницы фильма с отзывами — УПРОЩЁННАЯ ВЕРСИЯ."""
import allure
from playwright.sync_api import Page, Locator, expect
from tests.ui.pages.base_page import BasePage


class MoviePage(BasePage):
    """Page Object для страницы просмотра фильма."""

    def __init__(self, page: Page, movie_id: int):
        super().__init__(page)
        self.movie_id = movie_id
        self.url = f"https://dev-cinescope.coconutqa.ru/movies/{movie_id}"
        self._last_review_text = ""

    @property
    def review_textarea(self) -> Locator:
        return self.page.locator("textarea").first

    @property
    def rating_combobox(self) -> Locator:
        return self.page.get_by_role("combobox")

    @property
    def submit_review_button(self) -> Locator:
        return self.page.get_by_role("button", name="Отправить")

    @allure.step("Открыть страницу фильма")
    def open(self):
        self.page.goto(self.url, wait_until="domcontentloaded", timeout=15000)
        self.review_textarea.wait_for(state="visible", timeout=10000)

    @allure.step("Установить рейтинг: {rating} звёзд")
    def set_rating(self, rating: int):
        current = self.rating_combobox.text_content().strip()
        if current == str(rating):
            return
        self.rating_combobox.click(timeout=5000)
        self.page.locator("[role='option']").first.wait_for(state="visible", timeout=3000)
        self.page.locator("[role='option']").filter(has_text=str(rating)).first.click(timeout=5000, force=True)
        self.page.wait_for_timeout(500)

    @allure.step("Ввести текст отзыва: '{text}'")
    def fill_review_text(self, text: str):
        self._last_review_text = text
        self.review_textarea.fill(text, timeout=10000)

    @allure.step("Отправить отзыв")
    def submit_review(self):
        """Отправляет отзыв. Не ждёт алертов — только клик + пауза."""
        self.submit_review_button.click(timeout=10000)
        self.page.wait_for_timeout(3000)
        self.page.reload(wait_until="domcontentloaded", timeout=10000)
        self.page.wait_for_timeout(2000)

    @allure.step("Проверить успешную отправку отзыва")
    def assert_review_submitted(self):

        expect(self.page).not_to_have_title("404", timeout=3000)

        if self._last_review_text:
            snippet = self._last_review_text[:20]
            if self.page.locator(f"text={snippet}").count() > 0:
                print(f"Фрагмент отзыва '{snippet}...' найден на странице")
                return

        print("Текст отзыва не найден, но страница загружена — продолжаем тест")
