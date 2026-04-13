from dataclasses import dataclass
from typing import List
from datetime import datetime


@dataclass
class UserResponse:
    """Модель ответа с данными пользователя."""
    id: str
    email: str
    full_name: str
    roles: List[str]
    verified: bool
    banned: bool
    created_at: datetime

    @classmethod
    def from_dict(cls, data: dict) -> 'UserResponse':
        """Создаёт модель из словаря ответа API."""
        return cls(
            id=data['id'],
            email=data['email'],
            full_name=data['fullName'],
            roles=data.get('roles', []),
            verified=data.get('verified', False),
            banned=data.get('banned', False),
            created_at=datetime.fromisoformat(data['createdAt'].replace('Z', '+00:00'))
        )


@dataclass
class UserLocator:
    """Модель для поиска пользователя по ID или email."""
    value: str
    is_email: bool = False

    @classmethod
    def by_id(cls, user_id: str) -> 'UserLocator':
        return cls(value=user_id, is_email=False)

    @classmethod
    def by_email(cls, email: str) -> 'UserLocator':
        return cls(value=email, is_email=True)