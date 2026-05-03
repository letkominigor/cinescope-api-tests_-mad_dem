"""Page Object Models для Cinescope UI тестов."""
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


class CinescopeRegisterPage(BasePage):
    """Page Object для страницы регистрации."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.url = f"{self.home_url}register"

    @property
    def full_name_input(self) -> Locator:
        return self.page.locator("input[name='fullName']")

    @property
    def email_input(self) -> Locator:
        return self.page.locator("input[name='email']")

    @property
    def password_input(self) -> Locator:
        return self.page.locator("input[name='password']")

    @property
    def repeat_password_input(self) -> Locator:
        return self.page.locator("input[name='passwordRepeat']")

    @property
    def register_button(self) -> Locator:
        return self.page.locator("form").get_by_role("button", name="Зарегистрироваться")

    @property
    def sign_in_link(self) -> Locator:
        return self.page.get_by_role("link", name="Войти")

    # 🔹 Действия
    @allure.step("Открыть страницу регистрации")
    def open(self):
        self.page.goto(self.url)
        # Ждём, что форма загрузилась
        self.full_name_input.wait_for(state="visible", timeout=10000)

    @allure.step("Регистрация пользователя")
    def register(self, full_name: str, email: str, password: str, confirm_password: str):
        """Заполняет форму регистрации и отправляет."""
        self.full_name_input.fill(full_name, timeout=10000)
        self.email_input.fill(email, timeout=10000)
        self.password_input.fill(password, timeout=10000)
        self.repeat_password_input.fill(confirm_password, timeout=10000)

        with self.page.expect_navigation(timeout=15000):
            self.register_button.click(timeout=10000)

    @allure.step("Проверка редиректа на страницу входа")
    def assert_was_redirect_to_login_page(self):
        expect(self.page).to_have_url(f"{self.home_url}login", timeout=10000)

    @allure.step("Проверка появления алерта")
    def assert_alert_was_pop_up(self, expected_text: str = "Подтвердите свою почту"):
        alert = self.page.get_by_text(expected_text)
        expect(alert).to_be_visible(timeout=10000)
        expect(alert).to_be_hidden(timeout=10000)
