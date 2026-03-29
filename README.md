# Запустить все тесты фильмов
pytest tests/api/test_movie.py tests/api/test_movie_negative.py -v -s
# Запустить только позитивные
pytest tests/api/test_movie.py -v -s
# Запустить только тест на фильтры
pytest tests/api/test_movie.py::TestMoviesPositive::test_get_movies_filtered_by_location -v -s
# Запустить все тесты проекта
pytest tests/api/ -v -s

# показать 5 самых медленных тестов
pytest --durations=5
# порядок выполнения setup/teardown
pytest --setup-plan
# список доступных фикстур
pytest --fixtures
# список зарегистрированных маркеров
pytest --markers
# структура тестов без запуска
pytest --co
# запуск одного файла
pytest test_user_api.py
# подробный вывод
pytest -v
# краткий режим
pytest -q
# остановка на первом упавшем тесте
pytest -x
# запуск по имени (подстрока)
pytest -k create_user
# запуск всех тестов, где марка slow
pytest -m slow            