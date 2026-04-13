"""Pydantic модели для валидации ответов Movies API."""
from typing import List, Optional
from pydantic import BaseModel, Field


class MovieResponse(BaseModel):
    """Модель ответа для одного фильма."""
    id: int
    name: str
    price: float
    description: Optional[str] = None
    imageUrl: Optional[str] = None
    location: str
    published: bool
    rating: Optional[float] = None
    genreId: Optional[int] = None
    createdAt: str
    updatedAt: Optional[str] = None

    class Config:
        from_attributes = True


class MoviesListResponse(BaseModel):
    """Модель ответа для списка фильмов."""
    movies: List[MovieResponse]
    count: int

    class Config:
        from_attributes = True