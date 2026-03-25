"""Тесты на удаление фильмов с ролевой моделью."""
import pytest
from custom_requester.custom_requester import RequestError
from utils.data_generator import DataGenerator


class TestMovieDeleteByRole:
    """
    Параметризованные тесты на удаление фильмов.

    По документации: только SUPER_ADMIN может удалять фильмы.
    ADMIN и USER не имеют прав на удаление.
    """

    @pytest.mark.parametrize(
        "user_role, expected_status, should_succeed",
        [
            ("SUPER_ADMIN", 200, True),  # Может удалять
            ("ADMIN", 403, False),  # Не может удалять
            ("USER", 403, False),  # Не может удалять
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
        """
        Тест: удаление фильма пользователями с разными ролями.

        :param super_admin: фикстура супер-админа
        :param admin_user: фикстура админа
        :param common_user: фикстура обычного пользователя
        :param user_role: роль пользователя (SUPER_ADMIN, ADMIN, USER)
        :param expected_status: ожидаемый статус-код
        :param should_succeed: должен ли тест успешно удалить фильм
        """
        # Выбираем пользователя по роли
        user_map = {
            "SUPER_ADMIN": super_admin,
            "ADMIN": admin_user,
            "USER": common_user
        }
        current_user = user_map[user_role]

        # Создаём фильм через супер-админа (у всех есть права на создание)
        movie_data = DataGenerator.generate_movie_data()
        create_response = super_admin.api.movies_api.create_movie(
            movie_data,
            expected_status=201
        )
        movie_id = create_response.json()["id"]

        try:
            if should_succeed:
                delete_response = current_user.api.movies_api.delete_movie(
                    movie_id,
                    expected_status=expected_status
                )
                assert delete_response.status_code == expected_status

                # Проверяем, что фильм действительно удалён
                with pytest.raises(RequestError) as exc_info:
                    super_admin.api.movies_api.get_movie_by_id(
                        movie_id,
                        expected_status=200
                    )
                assert exc_info.value.response.status_code == 404

            else:
                # ADMIN/USER: удаление должно вернуть ошибку
                with pytest.raises(RequestError) as exc_info:
                    current_user.api.movies_api.delete_movie(
                        movie_id,
                        expected_status=200
                    )

                # Проверяем, что получили 403 (Forbidden)
                assert exc_info.value.response.status_code == expected_status, (
                    f"Ожидали {expected_status} для роли {user_role}, "
                    f"получили {exc_info.value.response.status_code}"
                )

        finally:
            #  Очистка - если фильм не был удалён, удаляем через супер-админа
            if not should_succeed:
                super_admin.api.movies_api.delete_movie(
                    movie_id,
                    expected_status=200
                )