from api.api_manager import ApiManager


class User:
    def __init__(self, email: str, password: str, roles: list, api: ApiManager):
        self.id = None
        self.email = email
        self.password = password
        self.roles = roles
        self.api = api

    @property # делает метод creds доступным как атрибут
    def creds(self):
        """Возвращает кортеж (email, password)"""
        return self.email, self.password