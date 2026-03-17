# Запустить все тесты фильмов
pytest tests/api/test_movie.py tests/api/test_movie_negative.py -v -s

# Запустить только позитивные
pytest tests/api/test_movie.py -v -s

# Запустить только тест на фильтры
pytest tests/api/test_movie.py::TestMoviesPositive::test_get_movies_filtered_by_location -v -s

# Запустить все тесты проекта
pytest tests/api/ -v -s