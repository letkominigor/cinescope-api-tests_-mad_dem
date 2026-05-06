"""Page Object для страницы фильма с отзывами."""
import allure
from playwright.sync_api import Page, Locator, expect
from tests.ui.pages.base_page import BasePage


class MoviePage(BasePage):
    """Page Object для страницы просмотра фильма."""

    def __init__(self, page: Page, movie_id: int):
        super().__init__(page)
        self.movie_id = movie_id
        self.url = f"https://dev-cinescope.coconutqa.ru/movies/{movie_id}"

    # Локаторы — под Tailwind CSS вёрстку
    @property
    def review_textarea(self) -> Locator:
        return self.page.locator("textarea").first

    @property
    def rating_combobox(self) -> Locator:
        return self.page.get_by_role("combobox")

    @property
    def submit_review_button(self) -> Locator:
        return self.page.get_by_role("button", name="Отправить")

    @property
    def review_list(self) -> Locator:
        """
        Список отзывов — под вёрстку с Tailwind CSS.
        Отзывы рендерятся в <p class="overflow-hidden text-ellipsis">
        """
        return self.page.locator("p.overflow-hidden, [class*='overflow-hidden']")

    @property
    def success_notification(self) -> Locator:
        """Уведомление об успешной отправке (если есть)."""
        return self.page.get_by_text("Отзыв успешно добавлен").or_(
            self.page.get_by_text("Спасибо за ваш отзыв")
        )

    # Действия — без wait_for_timeout() и reload()
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
        expect(self.rating_combobox).to_contain_text(str(rating), timeout=3000)

    @allure.step("Ввести текст отзыва")
    def fill_review_text(self, text: str):
        """Просто действие. Данные не сохраняются внутри PO."""
        self.review_textarea.fill(text, timeout=10000)
        expect(self.review_textarea).to_have_value(text, timeout=3000)

    @allure.step("Отправить отзыв")
    def submit_review(self):
        expect(self.submit_review_button).to_be_enabled(timeout=5000)

        with self.page.expect_response(lambda r: "review" in r.url.lower(), timeout=15000):
            self.submit_review_button.click(timeout=10000)


    @allure.step("Проверить успешную отправку отзыва")
    def assert_review_submitted(self, expected_text: str = None):
        """
        Реальная проверка: тест упадёт, если отзыв не найден.
        Ждём конкретные события, а не фиксированное время.
        """
        if expected_text is None and hasattr(self, '_last_review_text'):
            expected_text = self._last_review_text

        errors = []

        #  Критерий 1: Уведомление об успехе (если бэкенд его показывает)
        try:
            expect(self.success_notification.first).to_be_visible(timeout=10000)

            return
        except AssertionError as e:
            errors.append(f"Уведомление: {str(e)[:60]}")

        #  Критерий 2: Текст отзыва появился в списке (основной сценарий)
        if expected_text:
            try:
                snippet = expected_text[:20]
                review_in_list = self.review_list.filter(has_text=snippet).first
                expect(review_in_list).to_be_visible(timeout=10000)
                return
            except AssertionError as e:
                errors.append(f"Список отзывов: {str(e)[:60]}")

        #  Критерий 3: Фоллбэк — текст в любом элементе страницы
        if expected_text:
            try:
                snippet = expected_text[:15]
                expect(self.page.locator(f"text={snippet}").first).to_be_visible(timeout=5000)
                return
            except AssertionError as e:
                errors.append(f"Фоллбэк: {str(e)[:60]}")

        raise AssertionError(
            f"ПРОВЕРКА ОТЗЫВА НЕ ПРОЙДЕНА!\n"
            f"URL: {self.page.url}\n"
            f"Ожидаемый текст: '{expected_text[:30] if expected_text else 'N/A'}...'\n"
            f"Причины:\n" + "\n".join(f"  • {err}" for err in errors) +
            f"\n Подсказка: Проверь, что бэкенд действительно сохраняет отзыв.\n"
            f"   Открой DevTools → Network → найди POST /reviews → посмотри ответ."
        )

    @allure.step("Проверить, что отзыв отображается в списке")
    def assert_review_visible(self, expected_text: str):
        """Проверяет, что текст отзыва виден в списке отзывов."""
        snippet = expected_text[:20]
        expect(self.review_list.filter(has_text=snippet).first).to_be_visible(timeout=10000)
