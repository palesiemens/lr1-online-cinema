"""Сервисный слой: CRUD и контроль связей предметной области."""

from __future__ import annotations

from dataclasses import replace
from typing import Any, TypeVar

from .exceptions import BusinessRuleError, DuplicateEntityError
from .models import (
    CinemaData,
    Device,
    FavoriteList,
    Genre,
    Movie,
    Payment,
    PromoCode,
    Review,
    Subscription,
    SubscriptionPlan,
    User,
    WatchHistoryEntry,
)
from .repository import InMemoryRepository

T = TypeVar("T")
MODEL_TYPES: tuple[type[Any], ...] = (
    User,
    Genre,
    Movie,
    SubscriptionPlan,
    Subscription,
    Review,
    WatchHistoryEntry,
    FavoriteList,
    Payment,
    PromoCode,
    Device,
)


class CinemaService:
    """Предоставляет операции управления данными онлайн-кинотеатра."""

    def __init__(self) -> None:
        self._repositories: dict[type[Any], InMemoryRepository[Any]] = {
            model_type: InMemoryRepository(model_type.__name__)
            for model_type in MODEL_TYPES
        }

    def create(self, entity: T) -> T:
        """Добавляет объект после проверки уникальности и внешних связей."""
        model_type = type(entity)
        repository = self._repository_for(model_type)
        self._check_unique(entity)
        self._validate_relations(entity)
        return repository.add(entity)

    def get(self, model_type: type[T], entity_id: int) -> T:
        """Возвращает объект по идентификатору."""
        return self._repository_for(model_type).get(entity_id)

    def get_all(self, model_type: type[T]) -> list[T]:
        """Возвращает все объекты заданного типа."""
        return self._repository_for(model_type).get_all()

    def update(self, model_type: type[T], entity_id: int, **changes: Any) -> T:
        """Обновляет поля объекта, сохраняя его идентификатор."""
        if "id" in changes:
            raise BusinessRuleError("Изменение идентификатора запрещено.")
        repository = self._repository_for(model_type)
        current = repository.get(entity_id)
        updated = replace(current, **changes)
        self._check_unique(updated, exclude_id=entity_id)
        self._validate_relations(updated)
        return repository.update(entity_id, updated)

    def delete(self, model_type: type[T], entity_id: int) -> T:
        """Удаляет объект, если на него не ссылаются другие сущности."""
        repository = self._repository_for(model_type)
        entity = repository.get(entity_id)
        self._check_delete_restrictions(entity)
        return repository.delete(entity_id)

    def search_movies(self, query: str) -> list[Movie]:
        """Ищет фильмы по названию, описанию или имени режиссера."""
        normalized_query = query.strip().casefold()
        if not normalized_query:
            return self.get_all(Movie)
        return [
            movie
            for movie in self.get_all(Movie)
            if normalized_query in movie.title.casefold()
            or normalized_query in movie.description.casefold()
            or normalized_query in movie.director.casefold()
        ]

    def export_data(self) -> CinemaData:
        """Собирает текущее состояние репозиториев в единый объект данных."""
        return CinemaData(
            users=self.get_all(User),
            genres=self.get_all(Genre),
            movies=self.get_all(Movie),
            plans=self.get_all(SubscriptionPlan),
            subscriptions=self.get_all(Subscription),
            reviews=self.get_all(Review),
            watch_history=self.get_all(WatchHistoryEntry),
            favorite_lists=self.get_all(FavoriteList),
            payments=self.get_all(Payment),
            promo_codes=self.get_all(PromoCode),
            devices=self.get_all(Device),
        )

    def import_data(self, data: CinemaData) -> None:
        """Заменяет текущее состояние данными с повторной проверкой связей."""
        replacement = CinemaService()
        # Порядок важен: сначала создаются объекты, на которые ссылаются другие.
        ordered_collections: tuple[tuple[type[Any], list[Any]], ...] = (
            (User, data.users),
            (Genre, data.genres),
            (Movie, data.movies),
            (SubscriptionPlan, data.plans),
            (Subscription, data.subscriptions),
            (Review, data.reviews),
            (WatchHistoryEntry, data.watch_history),
            (FavoriteList, data.favorite_lists),
            (Payment, data.payments),
            (PromoCode, data.promo_codes),
            (Device, data.devices),
        )
        for _, entities in ordered_collections:
            for entity in entities:
                replacement.create(entity)
        self._repositories = replacement._repositories

    def _repository_for(self, model_type: type[T]) -> InMemoryRepository[T]:
        if model_type not in self._repositories:
            raise TypeError(f"Тип {model_type.__name__} не поддерживается сервисом.")
        return self._repositories[model_type]

    def _check_unique(self, entity: Any, exclude_id: int | None = None) -> None:
        """Проверяет уникальные бизнес-ключи отдельных сущностей."""
        if isinstance(entity, User):
            duplicates = [
                item for item in self.get_all(User)
                if item.email == entity.email and item.id != exclude_id
            ]
            if duplicates:
                raise DuplicateEntityError(
                    "Пользователь с такой почтой уже существует."
                )
        elif isinstance(entity, Genre):
            duplicates = [
                item for item in self.get_all(Genre)
                if (
                    item.name.casefold() == entity.name.casefold()
                    and item.id != exclude_id
                )
            ]
            if duplicates:
                raise DuplicateEntityError("Жанр с таким названием уже существует.")
        elif isinstance(entity, PromoCode):
            duplicates = [
                item for item in self.get_all(PromoCode)
                if item.code == entity.code and item.id != exclude_id
            ]
            if duplicates:
                raise DuplicateEntityError("Такой промокод уже существует.")

    def _validate_relations(self, entity: Any) -> None:
        """Проверяет внешние ключи и допустимость связей между объектами."""
        if isinstance(entity, Movie):
            for genre_id in entity.genre_ids:
                self.get(Genre, genre_id)
        elif isinstance(entity, Subscription):
            self.get(User, entity.user_id)
            self.get(SubscriptionPlan, entity.plan_id)
            # Изменение владельца не должно делать уже созданные платежи чужими.
            if any(
                payment.subscription_id == entity.id
                and payment.user_id != entity.user_id
                for payment in self.get_all(Payment)
            ):
                raise BusinessRuleError(
                    "Нельзя сменить владельца подписки: к ней привязан платеж "
                    "другого пользователя."
                )
        elif isinstance(entity, Review):
            self.get(User, entity.user_id)
            self.get(Movie, entity.movie_id)
            if any(
                item.user_id == entity.user_id and item.movie_id == entity.movie_id
                and item.id != entity.id
                for item in self.get_all(Review)
            ):
                raise BusinessRuleError("Пользователь уже оставил отзыв на этот фильм.")
        elif isinstance(entity, WatchHistoryEntry):
            self.get(User, entity.user_id)
            self.get(Movie, entity.movie_id)
        elif isinstance(entity, FavoriteList):
            self.get(User, entity.user_id)
            for movie_id in entity.movie_ids:
                self.get(Movie, movie_id)
        elif isinstance(entity, Payment):
            self.get(User, entity.user_id)
            subscription = self.get(Subscription, entity.subscription_id)
            if subscription.user_id != entity.user_id:
                raise BusinessRuleError(
                    "Платеж и подписка должны принадлежать одному пользователю."
                )
        elif isinstance(entity, Device):
            self.get(User, entity.user_id)

    def _check_delete_restrictions(self, entity: Any) -> None:
        """Не позволяет удалить объект, на который существуют ссылки."""
        references: list[str] = []
        if isinstance(entity, Genre):
            if any(entity.id in item.genre_ids for item in self.get_all(Movie)):
                references.append("фильмы")
        elif isinstance(entity, Movie):
            if any(item.movie_id == entity.id for item in self.get_all(Review)):
                references.append("отзывы")
            if any(
                item.movie_id == entity.id
                for item in self.get_all(WatchHistoryEntry)
            ):
                references.append("история просмотров")
            if any(entity.id in item.movie_ids for item in self.get_all(FavoriteList)):
                references.append("списки избранного")
        elif isinstance(entity, User):
            linked_types = (
                Subscription, Review, WatchHistoryEntry, FavoriteList, Payment, Device
            )
            for linked_type in linked_types:
                if any(item.user_id == entity.id for item in self.get_all(linked_type)):
                    references.append(linked_type.__name__)
        elif isinstance(entity, SubscriptionPlan):
            if any(item.plan_id == entity.id for item in self.get_all(Subscription)):
                references.append("подписки")
        elif isinstance(entity, Subscription):
            if any(item.subscription_id == entity.id for item in self.get_all(Payment)):
                references.append("платежи")

        if references:
            joined = ", ".join(references)
            raise BusinessRuleError(
                f"Нельзя удалить {type(entity).__name__} id={entity.id}: "
                f"объект используется в данных ({joined})."
            )
