"""Пользовательские исключения приложения онлайн-кинотеатра."""


class CinemaError(Exception):
    """Базовое исключение предметной области онлайн-кинотеатра."""


class ValidationError(CinemaError):
    """Ошибка проверки значений объекта или входных данных."""


class EntityNotFoundError(CinemaError):
    """Запрашиваемая сущность отсутствует в хранилище."""


class DuplicateEntityError(CinemaError):
    """Попытка добавить сущность с уже используемым идентификатором или ключом."""


class BusinessRuleError(CinemaError):
    """Операция нарушает бизнес-правило или целостность связей."""


class StorageError(CinemaError):
    """Ошибка чтения, записи или разбора файла данных."""
