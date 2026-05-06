"""Page Object для страницы входа."""

import allure
from playwright.sync_api import Page, Locator, expect
from tests.ui.pages.base_page import BasePage

class CinescopeLoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.url = f"{self.home_url}login"

    @property
    def email_input(self) -> Locator:
        return self.page.get_by_label("Email")

    @property
    def password_input(self) -> Locator:
        return self.page.get_by_label("Пароль")

    @property
    def login_button(self) -> Locator:
        return self.page.locator("form").get_by_role("button", name="Войти")

    @property
    def register_link(self) -> Locator:
        return self.page.get_by_role("link", name="Зарегистрироваться")

    @allure.step("Открыть страницу входа")
    def open(self):
        self.page.goto(self.url)

    @allure.step("Вход в систему")
    def login(self, email: str, password: str):
        self.email_input.fill(email)
        self.password_input.fill(password)
        with self.page.expect_navigation(timeout=10000):
            self.login_button.click()

    @allure.step("Проверка редиректа на главную")
    def assert_was_redirect_to_home_page(self):
        expect(self.page).to_have_url(self.home_url, timeout=10000)

    @allure.step("Проверка алерта")
    def assert_alert_was_pop_up(self, expected_text: str = "Вы вошли в аккаунт"):
        alert = self.page.get_by_text(expected_text)
        expect(alert).to_be_visible(timeout=5000)
        expect(alert).to_be_hidden(timeout=10000)
