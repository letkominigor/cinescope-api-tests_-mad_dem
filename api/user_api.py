from constants.constants import BASE_URL_AUTH
from custom_requester.custom_requester import CustomRequester

# Этот класс работает с информацией о пользователях

class UserAPI(CustomRequester):
    """Класс для работы с пользователями."""

    def __init__(self, session):
        super().__init__(session=session, base_url=BASE_URL_AUTH.strip())

    def create_user(self, user_data, expected_status=201):
        """Создание пользователя."""
        return self.send_request(
            method="POST",
            endpoint="/user",
            data=user_data,
            expected_status=expected_status
        )

    def get_user(self, user_locator,expected_status=200):
        return self.send_request(
            "GET", f"/user/{user_locator}",
            expected_status=expected_status
        )


    """def get_user_info(self, user_id, expected_status=200):
        return self.send_request(
            "GET",
            f"/user/{user_id}",
            expected_status=expected_status
        )"""

    def delete_user(self, user_id, expected_status=200):
        """
        Удаление пользователя.
        :param user_id: ID пользователя.
        :param expected_status: Ожидаемый статус-код.
        """
        return self.send_request(
            method="DELETE",
            endpoint=f"/user/{user_id}",
            expected_status=expected_status
        )