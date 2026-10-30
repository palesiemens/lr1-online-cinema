"""Универсальное хранилище объектов в оперативной памяти."""

from __future__ import annotations

from typing import Generic, TypeVar

from .exceptions import DuplicateEntityError, EntityNotFoundError

T = TypeVar("T")


class InMemoryRepository(Generic[T]):
    """Реализует базовые операции CRUD для объектов с целочисленным id."""

    def __init__(self, entity_name: str) -> None:
        self._entity_name = entity_name
        self._items: dict[int, T] = {}

    def add(self, entity: T) -> T:
        entity_id = int(getattr(entity, "id"))
        if entity_id in self._items:
            raise DuplicateEntityError(
                f"{self._entity_name} с id={entity_id} уже существует."
            )
        self._items[entity_id] = entity
        return entity

    def get(self, entity_id: int) -> T:
        try:
            return self._items[entity_id]
        except KeyError as exc:
            raise EntityNotFoundError(
                f"{self._entity_name} с id={entity_id} не найден(а)."
            ) from exc

    def get_all(self) -> list[T]:
        return [self._items[key] for key in sorted(self._items)]

    def update(self, entity_id: int, entity: T) -> T:
        if entity_id not in self._items:
            raise EntityNotFoundError(
                f"{self._entity_name} с id={entity_id} не найден(а)."
            )
        if int(getattr(entity, "id")) != entity_id:
            raise ValueError("Идентификатор объекта нельзя изменить при обновлении.")
        self._items[entity_id] = entity
        return entity

    def delete(self, entity_id: int) -> T:
        try:
            return self._items.pop(entity_id)
        except KeyError as exc:
            raise EntityNotFoundError(
                f"{self._entity_name} с id={entity_id} не найден(а)."
            ) from exc

    def clear(self) -> None:
        self._items.clear()

    def __len__(self) -> int:
        return len(self._items)
