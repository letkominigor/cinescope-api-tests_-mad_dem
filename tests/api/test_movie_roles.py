"""Тесты на удаление фильмов с ролевой моделью."""
import pytest
import allure
from custom_requester.custom_requester import RequestError
from utils.data_generator import DataGenerator
from constants.constants import STATUS_OK, STATUS_FORBIDDEN, STATUS_CREATED


@allure.feature("Movies API")
@allure.story("Права доступа (RBAC)")
@allure.label("qa_name", "Komin Igor")
@allure.label("layer", "api")
class TestMovieDeleteByRole:
    """Параметризованные тесты на удаление фильмов."""

    @allure.title("Удаление фильма пользователями с разными ролями")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.api
    @pytest.mark.roles
    @pytest.mark.parametrize(
        "user_role, expected_status, should_succeed",
        [
            ("SUPER_ADMIN", STATUS_OK, True),
            ("ADMIN", STATUS_FORBIDDEN, False),
            ("USER", STATUS_FORBIDDEN, False),
        ],
        ids=["super_admin", "admin", "user"]
    )
    def test_delete_movie_by_role(
        self,
        super_admin,
        admin_user,
        common_user,
        user_role: str,
        expected_status: int,
        should_succeed: bool
    ):
        """Тест: удаление фильма пользователями с разными ролями."""
        # Arrange
        user_map = {
            "SUPER_ADMIN": super_admin,
            "ADMIN": admin_user,
            "USER": common_user
        }
        current_user = user_map[user_role]

        with allure.step("Создаём тестовый фильм через супер-админа"):
            movie_data = DataGenerator.generate_movie_data()
            create_response = super_admin.api.movies_api.create_movie(
                movie_data,
                expected_status=STATUS_CREATED
            )
            movie_id = create_response.json()["id"]

        try:
            if should_succeed:
                # SUPER_ADMIN: удаление должно пройти успешно
                with allure.step(f"{user_role} удаляет фильм (ожидаем успех)"):
                    delete_response = current_user.api.movies_api.delete_movie(
                        movie_id,
                        expected_status=expected_status
                    )
                    assert delete_response.status_code == expected_status

                with allure.step("Проверяем, что фильм удалён"):
                    with pytest.raises(RequestError) as exc_info:
                        super_admin.api.movies_api.get_movie_by_id(
                            movie_id,
                            expected_status=STATUS_OK
                        )
                    assert exc_info.value.response.status_code == 404

            else:
                # ADMIN/USER: удаление должно вернуть ошибку
                with allure.step(f"{user_role} пытается удалить фильм (ожидаем отказ)"):
                    with pytest.raises(RequestError) as exc_info:
                        current_user.api.movies_api.delete_movie(
                            movie_id,
                            expected_status=STATUS_OK  # Не ожидаем успеха
                        )
                    assert exc_info.value.response.status_code == expected_status, (
                        f"Ожидали {expected_status} для роли {user_role}, "
                        f"получили {exc_info.value.response.status_code}"
                    )

        finally:
            # Cleanup: удаляем фильм если он ещё существует (только если не был удалён)
            if not should_succeed:
                with allure.step("Очистка: удаляем тестовый фильм"):
                    super_admin.api.movies_api.delete_movie(
                        movie_id,
                        expected_status=STATUS_OK
                    )