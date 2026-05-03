"""Обёртка над запросами."""
import json
import logging
import os
from urllib.parse import urlencode
from pydantic import BaseModel
from constants.constants import GREEN, RESET, RED

class RequestError(ValueError):
    """Кастомное исключение с сохранением ответа."""
    def __init__(self, message, response=None):
        super().__init__(message)
        self.response = response

class CustomRequester:
    """Кастомный реквестер для стандартизации HTTP-запросов."""

    base_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    def __init__(self, session, base_url):
        self.session = session
        self.base_url = base_url
        self.headers = self.base_headers.copy()
        self._update_session_headers(**self.headers)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def send_request(self, method, endpoint, data=None, expected_status=200, need_logging=True, params=None):
        url = f"{self.base_url}{endpoint}"
        if params:
            query_string = urlencode(params)
            url = f"{url}?{query_string}"

        if isinstance(data, BaseModel):
            data = json.loads(data.model_dump_json(exclude_unset=True))

        response = self.session.request(method, url, json=data, headers=self.headers)

        if need_logging:
            self.log_request_and_response(response)

        if response.status_code != expected_status:
            raise RequestError(
                f"Unexpected status code: {response.status_code}. Expected: {expected_status}",
                response=response
            )
        return response

    def log_request_and_response(self, response):
        try:
            request = response.request
            headers = " \\\n".join([f"-H '{header}: {value}'" for header, value in request.headers.items()])
            full_test_name = f"pytest {os.environ.get('PYTEST_CURRENT_TEST', '').replace(' (call)', '')}"

            body = ""
            if hasattr(request, 'body') and request.body is not None:
                if isinstance(request.body, bytes):
                    body = request.body.decode('utf-8')
                elif isinstance(request.body, str):
                    body = request.body
                body = f"-d '{body}'\n" if body != '{}' else ''

            self.logger.info(
                f"{GREEN}{full_test_name}{RESET}\n"
                f"curl -X {request.method} '{request.url}' \\\n"
                f"{headers} \\\n"
                f"{body}"
            )

            response_status = response.status_code
            is_success = response.ok
            response_data = response.text
            if not is_success:
                self.logger.info(
                    f"\tRESPONSE:\nSTATUS_CODE: {RED}{response_status}{RESET}\nDATA: {RED}{response_data}{RESET}"
                )
        except Exception as e:
            self.logger.info(f"\nLogging went wrong: {type(e)} - {e}")

    def _update_session_headers(self, **kwargs):
        self.headers.update(kwargs)
        self.session.headers.update(kwargs)