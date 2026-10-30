"""Демонстрационный набор данных для проверки приложения."""

from .models import (
    CinemaData,
    Device,
    FavoriteList,
    Genre,
    Movie,
    Payment,
    PaymentStatus,
    PromoCode,
    Review,
    Subscription,
    SubscriptionPlan,
    SubscriptionStatus,
    User,
    WatchHistoryEntry,
)
from .service import CinemaService


def build_sample_data() -> CinemaData:
    """Создает согласованный демонстрационный набор данных."""
    return CinemaData(
        users=[
            User(1, "Иван Петров", "ivan@example.com"),
            User(2, "Елена Смирнова", "elena@example.com"),
        ],
        genres=[
            Genre(1, "Фантастика", "Научная фантастика и космические истории."),
            Genre(2, "Триллер", "Напряженные истории и расследования."),
            Genre(3, "Драма", "Истории о людях и важных решениях."),
        ],
        movies=[
            Movie(
                1,
                "Последний сигнал",
                "Инженер получает сообщение, которое было отправлено из будущего.",
                2024,
                118,
                "16+",
                [1, 2],
                "А. Воронов",
                ["М. Орлова", "И. Соколов"],
            ),
            Movie(
                2,
                "Город без сна",
                "Журналист расследует серию загадочных событий в большом городе.",
                2023,
                104,
                "16+",
                [2, 3],
                "Е. Миронова",
                ["А. Лебедев", "Н. Ким"],
            ),
            Movie(
                3,
                "Точка возврата",
                "Путешественник пытается восстановить отношения с семьей.",
                2022,
                96,
                "12+",
                [3],
                "Д. Волков",
                ["С. Белова", "П. Назаров"],
            ),
        ],
        plans=[
            SubscriptionPlan(1, "Стандарт", 299.0, 30, 2, "Full HD"),
            SubscriptionPlan(2, "Премиум", 499.0, 30, 5, "4K"),
        ],
        subscriptions=[
            Subscription(
                1, 1, 1, "2026-10-01", "2026-11-01", SubscriptionStatus.ACTIVE
            )
        ],
        reviews=[
            Review(
                1, 1, 1, 9, "Интересный сюжет и хорошая динамика.",
                "2026-10-10T18:30:00"
            )
        ],
        watch_history=[
            WatchHistoryEntry(1, 1, 1, 3540, "2026-10-29T21:15:00"),
            WatchHistoryEntry(2, 1, 3, 1200, "2026-10-25T20:05:00"),
        ],
        favorite_lists=[FavoriteList(1, 1, "Посмотреть позже", [2, 3])],
        payments=[
            Payment(
                1, 1, 1, 299.0, "Банковская карта", PaymentStatus.PAID,
                "2026-10-01T09:00:00"
            )
        ],
        promo_codes=[PromoCode(1, "START20", 20, "2026-12-31", True)],
        devices=[Device(1, 1, "Домашний телевизор", "smart_tv", "2026-10-29T21:00:00")],
    )


def create_sample_service() -> CinemaService:
    """Создает сервис и заполняет его демонстрационными данными."""
    service = CinemaService()
    service.import_data(build_sample_data())
    return service
