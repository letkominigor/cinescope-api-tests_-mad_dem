"""Константы для API тестов."""

# Цвета для логирования
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
MAGENTA = '\033[35m'
CYAN = '\033[36m'
RESET = '\033[0m'

# Auth API
BASE_URL_AUTH = "https://auth.dev-cinescope.coconutqa.ru"
LOGIN_ENDPOINT = "/login"
REGISTER_ENDPOINT = "/register"

# Movies API
BASE_URL_MOVIES = "https://api.dev-cinescope.coconutqa.ru"
MOVIES_ENDPOINT = "/movies"

# User API
BASE_URL_USER = "https://auth.dev-cinescope.coconutqa.ru"

# Headers
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# Статус-коды
STATUS_OK = 200
STATUS_CREATED = 201
STATUS_NO_CONTENT = 204
STATUS_BAD_REQUEST = 400
STATUS_UNAUTHORIZED = 401
STATUS_FORBIDDEN = 403
STATUS_NOT_FOUND = 404
STATUS_INTERNAL_ERROR = 500
