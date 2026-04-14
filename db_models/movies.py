"""Модель фильма для SQLAlchemy."""
from sqlalchemy import Column, String, Float, Boolean, DateTime, text
from sqlalchemy.orm import declarative_base
from typing import Dict, Any
from datetime import datetime, timezone

Base = declarative_base()


class MovieDBModel(Base):
    """Модель фильма"""

    __tablename__ = 'movies'

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    description = Column(String)
    image_url = Column(String)
    location = Column(String, nullable=False)
    published = Column(Boolean, default=False)
    rating = Column(Float)
    genre_id = Column(String)

    # UTC время: комбинация Python + PostgreSQL
    created_at = Column(
        DateTime,
        # Python fallback (для тестов)
        default=lambda: datetime.now(timezone.utc),
        # PostgreSQL primary (для продакшена)
        server_default=text("NOW() AT TIME ZONE 'UTC'"),
        nullable=False
    )

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'description': self.description,
            'image_url': self.image_url,
            'location': self.location,
            'published': self.published,
            'rating': self.rating,
            'genre_id': self.genre_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<Movie(id='{self.id}', name='{self.name}', price={self.price})>"