from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class RegisterRequest:
    """Модель запроса на регистрацию пользователя."""
    email: str
    fullName: str
    password: str
    passwordRepeat: str
    roles: List[str]
    verified: bool = True
    banned: bool = False


@dataclass
class LoginRequest:
    """Модель запроса на авторизацию."""
    email: str
    password: str


@dataclass
class AuthResponse:
    """Модель ответа авторизации."""
    user_id: str
    email: str
    full_name: str
    roles: List[str]
    access_token: str
    refresh_token: str
    expires_in: int
    verified: Optional[bool] = None
    banned: Optional[bool] = None
    created_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: dict, tokens: Optional[dict] = None) -> 'AuthResponse':
        """Создаёт модель из словаря ответа API."""
        user = data.get('user', data) 
        return cls(
            user_id=user.get('id'),
            email=user.get('email'),
            full_name=user.get('fullName'),
            roles=user.get('roles', []),
            verified=user.get('verified'),
            banned=user.get('banned'),
            created_at=datetime.fromisoformat(user['createdAt'].replace('Z', '+00:00'))
                if user.get('createdAt') else None,
            access_token=tokens.get('accessToken') if tokens else '',
            refresh_token=tokens.get('refreshToken') if tokens else '',
            expires_in=tokens.get('expiresIn') if tokens else 0
        )