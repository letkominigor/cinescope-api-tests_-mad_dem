"""Тесты страницы регистрации."""
import allure
from playwright.sync_api import Page
from utils.data_generator import DataGenerator
from models.page_object_models import CinescopeRegisterPage


@allure.feature("UI Tests")
@allure.story("Регистрация")
class TestRegisterPage:

    @allure.title("Проведение успешной регистрации")
    def test_register_by_ui(self, page: Page):
        """Регистрирует нового пользователя через UI и проверяет редирект."""
        random_email = DataGenerator.generate_random_email()
        random_name = DataGenerator.generate_random_name()
        random_password = DataGenerator.generate_random_password()

        register_page = CinescopeRegisterPage(page)

        register_page.open()
        register_page.register(
            full_name=f"PlaywrightTest {random_name}",
            email=random_email,
            password=random_password,
            confirm_password=random_password
        )

        register_page.assert_was_redirect_to_login_page()
        register_page.assert_alert_was_pop_up("Подтвердите свою почту")
