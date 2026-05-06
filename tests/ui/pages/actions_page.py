"""Универсальные действия для UI-тестов."""
import allure
from playwright.sync_api import Page, Locator, expect


class PageAction:
    def __init__(self, page: Page):
        self.page = page

    @allure.step("Переход на страницу: {url}")
    def open_url(self, url: str):
        self.page.goto(url)

    @allure.step("Ввод текста '{text}' в поле")
    def enter_text_to_element(self, locator: Locator | str, text: str):
        """Принимает Locator-объект или строку-селектор."""
        element = locator if isinstance(locator, Locator) else self.page.locator(locator)
        element.fill(text)

    @allure.step("Клик по элементу")
    def click_element(self, locator: Locator | str, timeout: int = 10000):
        element = locator if isinstance(locator, Locator) else self.page.locator(locator)
        element.click(timeout=timeout)

    @allure.step("Ожидание перехода на URL: {url}")
    def wait_redirect_for_url(self, url: str, timeout: int = 10000):
        self.page.wait_for_url(url, timeout=timeout)
        expect(self.page).to_have_url(url, timeout=timeout)

    @allure.step("Получение текста элемента")
    def get_element_text(self, locator: Locator | str) -> str:
        element = locator if isinstance(locator, Locator) else self.page.locator(locator)
        return element.text_content(timeout=5000)

    @allure.step("Ожидание видимости элемента")
    def wait_for_element(self, locator: Locator | str, state: str = "visible", timeout: int = 10000):
        element = locator if isinstance(locator, Locator) else self.page.locator(locator)
        element.wait_for(state=state, timeout=timeout)

    @allure.step("Скриншот страницы")
    def make_screenshot_and_attach_to_allure(self, name: str = "Screenshot"):
        screenshot = self.page.screenshot(full_page=True)
        allure.attach(screenshot, name=name, attachment_type=allure.attachment_type.PNG)

    @allure.step("Проверка всплывающего сообщения")
    def check_pop_up_element_with_text(self, text: str, timeout: int = 10000):
        """Проверяет появление и исчезновение алерта с текстом."""
        alert = self.page.get_by_text(text)

        with allure.step(f"Ожидание появления: '{text}'"):
            expect(alert).to_be_visible(timeout=timeout)

        with allure.step(f"Ожидание исчезновения: '{text}'"):\
            expect(alert).to_be_hidden(timeout=timeout)
