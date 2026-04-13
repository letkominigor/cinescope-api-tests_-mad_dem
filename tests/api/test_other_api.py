"""Тесты для дополнительных эндпоинтов (транзакции, прочее)."""
import random
import pytest
import allure
from sqlalchemy.orm import Session
from db_models.account import AccountTransactionTemplate
from utils.data_generator import DataGenerator


@allure.epic("Тестирование транзакций")
@allure.feature("Транзакции между счетами")
@allure.label("qa_name", "Komin Igor")
@allure.label("layer", "db")
class TestAccountTransactionTemplate:
    """Тесты для работы с аккаунтами и транзакциями."""

    @allure.story("Корректность перевода денег между счетами")
    @allure.description("""
    Этот тест проверяет корректность перевода денег между двумя счетами.
    Шаги:
    1. Создание двух счетов: Stan и Bob.
    2. Перевод 200 единиц от Stan к Bob.
    3. Проверка изменения балансов.
    4. Очистка тестовых данных.
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.db
    @pytest.mark.positive
    @allure.title("Тест перевода денег между счетами")
    def test_accounts_transaction_template(self, db_session: Session):
        """Тест корректного перевода денег между двумя счетами"""
        #  Arrange
        with allure.step("Создание тестовых данных в базе: счета Stan и Bob"):
            stan_user = f"Stan_{DataGenerator.generate_random_int(1000, 9999)}"
            bob_user = f"Bob_{DataGenerator.generate_random_int(1000, 9999)}"

            stan = AccountTransactionTemplate(user=stan_user, balance=1000)
            bob = AccountTransactionTemplate(user=bob_user, balance=500)

            db_session.add_all([stan, bob])
            db_session.commit()

        def transfer_money(session, from_user, to_user, amount):
            """Функция перевода денег (имитация бизнес-логики)"""
            with allure.step("Получаем счета из БД"):
                from_account = session.query(AccountTransactionTemplate).filter_by(user=from_user).one()
                to_account = session.query(AccountTransactionTemplate).filter_by(user=to_user).one()

            with allure.step("Проверяем достаточность средств"):
                if from_account.balance < amount:
                    raise ValueError("Недостаточно средств на счете")

            with allure.step("Выполняем перевод"):
                from_account.balance -= amount
                to_account.balance += amount

            with allure.step("Сохраняем изменения"):
                session.commit()

        #  Act & Assert
        with allure.step("Проверяем начальные балансы"):
            assert stan.balance == 1000, f"Баланс Stan: {stan.balance} != 1000"
            assert bob.balance == 500, f"Баланс Bob: {bob.balance} != 500"

        try:
            with allure.step("Выполняем перевод 200 единиц от Stan к Bob"):
                transfer_money(db_session, from_user=stan_user, to_user=bob_user, amount=200)

            with allure.step("Проверяем, что балансы изменились корректно"):
                # Обновляем объекты из БД
                db_session.refresh(stan)
                db_session.refresh(bob)

                assert stan.balance == 800, f"Баланс Stan: {stan.balance} != 800"
                assert bob.balance == 700, f"Баланс Bob: {bob.balance} != 700"

        except Exception as e:
            with allure.step("ОШИБКА: откат транзакции"):
                db_session.rollback()
            pytest.fail(f"Ошибка при переводе денег: {e}")

        finally:
            with allure.step("Удаляем тестовые данные из базы"):
                db_session.delete(stan)
                db_session.delete(bob)
                db_session.commit()

    @allure.story("Тест с автоматическими перезапусками")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.flaky(reruns=3, reruns_delay=1)
    @pytest.mark.api
    @allure.title("Тест с перезапусками при нестабильности")
    def test_with_retries(self):
        """Тест демонстрирующий работу маркера flaky для нестабильных тестов"""
        with allure.step("Шаг 1: Генерация случайного значения"):
            result = random.choice([True, False])

        with allure.step("Шаг 2: Проверка результата"):
            # Этот тест может падать случайно, но @pytest.mark.flaky позволит перезапустить его
            assert result, "Тест упал, потому что результат False (это ожидаемо для демонстрации flaky)"