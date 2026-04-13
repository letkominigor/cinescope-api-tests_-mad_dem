"""Тест подключения к БД"""
from db_requester.db_client import get_db_session
from sqlalchemy import text

class TestDBConnection:
    def test_db_server_info(self):
        with get_db_session() as session:
            result = session.execute(text("SELECT version()")).fetchone()
            assert result[0].startswith('PostgreSQL')
    
    def test_movies_count(self):
        with get_db_session() as session:
            count = session.execute(text("SELECT COUNT(*) FROM movies")).fetchone()[0]
            assert count >= 0
