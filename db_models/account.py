"""Модели для работы с таблицами аккаунтов."""
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class AccountTransactionTemplate(Base):
    """
    Модель тестового аккаунта для транзакций.
    Таблица в БД с полями: user, balance
    """
    __tablename__ = 'accounts_transaction_template'

    user = Column(String, primary_key=True)
    balance = Column(Integer, nullable=False, default=0)

    def __repr__(self):
        return f"<AccountTransactionTemplate(user='{self.user}', balance={self.balance})>"