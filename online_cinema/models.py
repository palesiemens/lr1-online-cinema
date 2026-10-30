"""Модели предметной области онлайн-кинотеатра."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields
from datetime import date, datetime
from enum import Enum
import math
import re
from typing import Any, TypeVar, get_args, get_origin, get_type_hints

from .exceptions import ValidationError


class SubscriptionStatus(str, Enum):
    """Состояние пользовательской подписки."""

    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class PaymentStatus(str, Enum):
    """Состояние платежа."""

    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


def _check_integer(value: int, field_name: str, minimum: int | None = None) -> None:
    """Проверяет, что значение является целым числом и не ниже минимума."""
    if type(value) is not int:
        raise ValidationError(f"Поле «{field_name}» должно быть целым числом.")
    if minimum is not None and value < minimum:
        raise ValidationError(
            f"Поле «{field_name}» должно быть не меньше {minimum}."
        )


def _check_positive(value: int, field_name: str) -> None:
    _check_integer(value, field_name, minimum=1)


def _check_amount(value: int | float, field_name: str) -> None:
    """Проверяет конечное неотрицательное числовое значение."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValidationError(f"Поле «{field_name}» должно быть числом.")
    if (isinstance(value, float) and not math.isfinite(value)) or value < 0:
        raise ValidationError(
            f"Поле «{field_name}» должно быть конечным и неотрицательным."
        )


def _check_bool(value: bool, field_name: str) -> None:
    if type(value) is not bool:
        raise ValidationError(f"Поле «{field_name}» должно быть логическим.")


def _check_text(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"Поле «{field_name}» не должно быть пустым.")


def _check_iso_date(value: str, field_name: str) -> None:
    try:
        date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError(
            f"Поле «{field_name}» должно содержать дату в формате ГГГГ-ММ-ДД."
        ) from exc


def _check_iso_datetime(value: str, field_name: str) -> None:
    try:
        datetime.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError(
            f"Поле «{field_name}» должно содержать дату и время ISO 8601."
        ) from exc


@dataclass(slots=True)
class Genre:
    """Жанр фильма."""

    id: int
    name: str
    description: str = ""

    def __post_init__(self) -> None:
        _check_positive(self.id, "id жанра")
        _check_text(self.name, "название жанра")


@dataclass(slots=True)
class Movie:
    """Карточка фильма в каталоге."""

    id: int
    title: str
    description: str
    release_year: int
    duration_minutes: int
    age_rating: str
    genre_ids: list[int] = field(default_factory=list)
    director: str = "Не указан"
    cast: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        _check_positive(self.id, "id фильма")
        _check_text(self.title, "название фильма")
        _check_text(self.description, "описание фильма")
        _check_integer(self.release_year, "год выпуска")
        if not 1888 <= self.release_year <= 2100:
            raise ValidationError(
                "Год выпуска должен находиться в диапазоне 1888-2100."
            )
        _check_positive(self.duration_minutes, "длительность фильма")
        if not isinstance(self.age_rating, str) or self.age_rating not in {
            "0+", "6+", "12+", "16+", "18+"
        }:
            raise ValidationError(
                "Возрастной рейтинг должен быть одним из: 0+, 6+, 12+, 16+, 18+."
            )
        if not isinstance(self.genre_ids, list) or any(
            type(value) is not int or value <= 0 for value in self.genre_ids
        ):
            raise ValidationError(
                "Идентификаторы жанров должны быть положительными целыми числами."
            )
        if len(self.genre_ids) != len(set(self.genre_ids)):
            raise ValidationError("Список жанров фильма не должен содержать повторов.")
        if not isinstance(self.cast, list) or any(
            not isinstance(name, str) or not name.strip() for name in self.cast
        ):
            raise ValidationError("Список актеров должен содержать непустые строки.")


@dataclass(slots=True)
class User:
    """Учетная запись зрителя."""

    id: int
    full_name: str
    email: str
    is_active: bool = True

    def __post_init__(self) -> None:
        _check_positive(self.id, "id пользователя")
        _check_text(self.full_name, "имя пользователя")
        _check_text(self.email, "электронная почта")
        self.email = self.email.strip().lower()
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", self.email):
            raise ValidationError("Указан некорректный адрес электронной почты.")
        _check_bool(self.is_active, "состояние учетной записи")


@dataclass(slots=True)
class SubscriptionPlan:
    """Тарифный план онлайн-кинотеатра."""

    id: int
    name: str
    price: float
    duration_days: int
    max_devices: int
    video_quality: str = "Full HD"

    def __post_init__(self) -> None:
        _check_positive(self.id, "id тарифа")
        _check_text(self.name, "название тарифа")
        _check_amount(self.price, "стоимость тарифа")
        _check_positive(self.duration_days, "срок действия тарифа")
        _check_positive(self.max_devices, "количество устройств")
        if not isinstance(self.video_quality, str) or self.video_quality not in {
            "HD", "Full HD", "4K"
        }:
            raise ValidationError("Качество видео должно быть HD, Full HD или 4K.")


@dataclass(slots=True)
class Subscription:
    """Подписка конкретного пользователя."""

    id: int
    user_id: int
    plan_id: int
    start_date: str
    end_date: str
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE

    def __post_init__(self) -> None:
        _check_positive(self.id, "id подписки")
        _check_positive(self.user_id, "id пользователя подписки")
        _check_positive(self.plan_id, "id тарифа подписки")
        _check_iso_date(self.start_date, "дата начала подписки")
        _check_iso_date(self.end_date, "дата окончания подписки")
        if date.fromisoformat(self.end_date) <= date.fromisoformat(self.start_date):
            raise ValidationError(
                "Дата окончания подписки должна быть позже даты начала."
            )
        try:
            self.status = SubscriptionStatus(self.status)
        except ValueError as exc:
            raise ValidationError("Неизвестный статус подписки.") from exc


@dataclass(slots=True)
class Review:
    """Оценка фильма, оставленная пользователем."""

    id: int
    user_id: int
    movie_id: int
    rating: int
    comment: str = ""
    created_at: str = field(
        default_factory=lambda: datetime.now().isoformat(timespec="seconds")
    )

    def __post_init__(self) -> None:
        _check_positive(self.id, "id отзыва")
        _check_positive(self.user_id, "id пользователя отзыва")
        _check_positive(self.movie_id, "id фильма отзыва")
        _check_integer(self.rating, "оценка фильма")
        if not 1 <= self.rating <= 10:
            raise ValidationError("Оценка фильма должна быть целым числом от 1 до 10.")
        if not isinstance(self.comment, str):
            raise ValidationError("Комментарий должен быть текстовой строкой.")
        _check_iso_datetime(self.created_at, "дата создания отзыва")


@dataclass(slots=True)
class WatchHistoryEntry:
    """Запись истории просмотра."""

    id: int
    user_id: int
    movie_id: int
    progress_seconds: int = 0
    watched_at: str = field(
        default_factory=lambda: datetime.now().isoformat(timespec="seconds")
    )

    def __post_init__(self) -> None:
        _check_positive(self.id, "id записи истории")
        _check_positive(self.user_id, "id пользователя истории")
        _check_positive(self.movie_id, "id фильма истории")
        _check_integer(self.progress_seconds, "прогресс просмотра", minimum=0)
        _check_iso_datetime(self.watched_at, "дата просмотра")


@dataclass(slots=True)
class FavoriteList:
    """Именованный список избранных фильмов пользователя."""

    id: int
    user_id: int
    name: str = "Избранное"
    movie_ids: list[int] = field(default_factory=list)

    def __post_init__(self) -> None:
        _check_positive(self.id, "id списка избранного")
        _check_positive(self.user_id, "id пользователя списка")
        _check_text(self.name, "название списка")
        if not isinstance(self.movie_ids, list) or any(
            type(value) is not int or value <= 0 for value in self.movie_ids
        ):
            raise ValidationError(
                "Идентификаторы фильмов должны быть положительными целыми числами."
            )
        if len(self.movie_ids) != len(set(self.movie_ids)):
            raise ValidationError(
                "В списке избранного не должно быть повторяющихся фильмов."
            )


@dataclass(slots=True)
class Payment:
    """Платеж за подписку."""

    id: int
    user_id: int
    subscription_id: int
    amount: float
    method: str
    status: PaymentStatus = PaymentStatus.PENDING
    created_at: str = field(
        default_factory=lambda: datetime.now().isoformat(timespec="seconds")
    )

    def __post_init__(self) -> None:
        _check_positive(self.id, "id платежа")
        _check_positive(self.user_id, "id пользователя платежа")
        _check_positive(self.subscription_id, "id подписки платежа")
        _check_amount(self.amount, "сумма платежа")
        _check_text(self.method, "способ оплаты")
        _check_iso_datetime(self.created_at, "дата платежа")
        try:
            self.status = PaymentStatus(self.status)
        except ValueError as exc:
            raise ValidationError("Неизвестный статус платежа.") from exc


@dataclass(slots=True)
class PromoCode:
    """Промокод для предоставления скидки."""

    id: int
    code: str
    discount_percent: int
    expires_at: str
    is_active: bool = True

    def __post_init__(self) -> None:
        _check_positive(self.id, "id промокода")
        _check_text(self.code, "код промокода")
        self.code = self.code.strip().upper()
        _check_bool(self.is_active, "активность промокода")
        _check_integer(self.discount_percent, "размер скидки")
        if not 1 <= self.discount_percent <= 100:
            raise ValidationError("Размер скидки должен быть от 1 до 100 процентов.")
        _check_iso_date(self.expires_at, "срок действия промокода")


@dataclass(slots=True)
class Device:
    """Устройство, с которого пользователь входит в сервис."""

    id: int
    user_id: int
    device_name: str
    device_type: str
    last_seen_at: str = field(
        default_factory=lambda: datetime.now().isoformat(timespec="seconds")
    )

    def __post_init__(self) -> None:
        _check_positive(self.id, "id устройства")
        _check_positive(self.user_id, "id пользователя устройства")
        _check_text(self.device_name, "название устройства")
        if not isinstance(self.device_type, str) or self.device_type not in {
            "smart_tv", "computer", "smartphone", "tablet", "other"
        }:
            raise ValidationError("Неизвестный тип устройства.")
        _check_iso_datetime(self.last_seen_at, "время последней активности")


T = TypeVar("T")


def _serialise(value: Any) -> Any:
    """Преобразует вложенные dataclass и Enum в типы JSON/XML."""
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, list):
        return [_serialise(item) for item in value]
    if isinstance(value, dict):
        return {key: _serialise(item) for key, item in value.items()}
    return value


def _coerce_value(value: Any, expected_type: Any) -> Any:
    """Восстанавливает тип поля после чтения JSON или XML."""
    origin = get_origin(expected_type)
    args = get_args(expected_type)

    if origin is list:
        item_type = args[0] if args else Any
        if value in (None, ""):
            return []
        if not isinstance(value, list):
            raise ValueError("Ожидался список значений.")
        return [_coerce_value(item, item_type) for item in value]
    if expected_type is Any:
        return value
    if isinstance(expected_type, type) and issubclass(expected_type, Enum):
        return expected_type(value)
    if expected_type is bool:
        if isinstance(value, bool):
            return value
        normalized = str(value).strip().lower()
        if normalized in {"true", "1", "yes"}:
            return True
        if normalized in {"false", "0", "no"}:
            return False
        raise ValueError(f"Некорректное логическое значение: {value!r}.")
    if expected_type is int:
        if type(value) is int:
            return value
        if isinstance(value, str):
            return int(value)
        raise ValueError(f"Ожидалось целое число, получено {value!r}.")
    if expected_type is float:
        if isinstance(value, bool) or not isinstance(value, (int, float, str)):
            raise ValueError(f"Ожидалось число, получено {value!r}.")
        return float(value)
    if expected_type is str:
        if not isinstance(value, str):
            raise ValueError(f"Ожидалась строка, получено {value!r}.")
        return value
    return value


@dataclass(slots=True)
class CinemaData:
    """Полный набор данных, переносимый между хранилищами."""

    users: list[User] = field(default_factory=list)
    genres: list[Genre] = field(default_factory=list)
    movies: list[Movie] = field(default_factory=list)
    plans: list[SubscriptionPlan] = field(default_factory=list)
    subscriptions: list[Subscription] = field(default_factory=list)
    reviews: list[Review] = field(default_factory=list)
    watch_history: list[WatchHistoryEntry] = field(default_factory=list)
    favorite_lists: list[FavoriteList] = field(default_factory=list)
    payments: list[Payment] = field(default_factory=list)
    promo_codes: list[PromoCode] = field(default_factory=list)
    devices: list[Device] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Возвращает сериализуемый словарь со всеми коллекциями."""
        return _serialise(asdict(self))

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> CinemaData:
        """Создает типизированные объекты из словаря, прочитанного из файла."""
        model_by_collection: dict[str, type[Any]] = {
            "users": User,
            "genres": Genre,
            "movies": Movie,
            "plans": SubscriptionPlan,
            "subscriptions": Subscription,
            "reviews": Review,
            "watch_history": WatchHistoryEntry,
            "favorite_lists": FavoriteList,
            "payments": Payment,
            "promo_codes": PromoCode,
            "devices": Device,
        }
        result: dict[str, Any] = {}
        for collection_name, model_type in model_by_collection.items():
            objects: list[Any] = []
            for raw_object in payload.get(collection_name, []):
                hints = get_type_hints(model_type)
                values = {
                    item.name: _coerce_value(raw_object[item.name], hints[item.name])
                    for item in fields(model_type)
                    if item.name in raw_object
                }
                objects.append(model_type(**values))
            result[collection_name] = objects
        return cls(**result)
