# Запустить все тесты фильмов
pytest tests/api/test_movie.py tests/api/test_movie_negative.py -v -s
# Запустить только позитивные
pytest tests/api/test_movie.py -v -s
# Запустить только тест на фильтры
pytest tests/api/test_movie.py::TestMoviesPositive::test_get_movies_filtered_by_location -v -s
# Запустить все тесты проекта
pytest tests/api/ -v -s


# Запуститьт все тесты с Allure
pytest tests/ --alluredir=./allure-results
# Только smoke-тесты
pytest -m smoke tests/api/test_user.py -v --alluredir=./allure-results
# Только тесты с БД
pytest -m db tests/api/test_other_api.py -v --alluredir=./allure-results
# Только параметризованные тесты
pytest -k "parametrize" tests/api/test_movie_filters.py -v --alluredir=./allure-results
# Исключить медленные тесты
pytest -m "not slow" tests/api/ -v --alluredir=./allure-results


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

# краткий режим
pytest -q
# остановка на первом упавшем тесте
pytest -x
# запуск по имени (подстрока)
pytest -k create_user
     