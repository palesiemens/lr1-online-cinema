"""Сериализация и десериализация набора данных в JSON и XML."""

from __future__ import annotations

from abc import ABC, abstractmethod
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from typing import Any

from .exceptions import StorageError
from .models import CinemaData


class StorageAdapter(ABC):
    """Общий интерфейс файлового хранилища."""

    @abstractmethod
    def save(self, data: CinemaData, path: str | Path) -> None:
        """Сохраняет набор данных в файл."""

    @abstractmethod
    def load(self, path: str | Path) -> CinemaData:
        """Загружает набор данных из файла."""


class JsonStorage(StorageAdapter):
    """Файловое хранилище формата JSON."""

    def save(self, data: CinemaData, path: str | Path) -> None:
        target = Path(path)
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                json.dumps(data.to_dict(), ensure_ascii=False, indent=4),
                encoding="utf-8",
            )
        except (OSError, TypeError, ValueError) as exc:
            raise StorageError(
                f"Не удалось сохранить JSON-файл {target}: {exc}"
            ) from exc

    def load(self, path: str | Path) -> CinemaData:
        target = Path(path)
        try:
            payload = json.loads(target.read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("Корневой элемент JSON должен быть объектом.")
            return CinemaData.from_dict(payload)
        except (OSError, json.JSONDecodeError, TypeError, ValueError, KeyError) as exc:
            raise StorageError(
                f"Не удалось загрузить JSON-файл {target}: {exc}"
            ) from exc


class XmlStorage(StorageAdapter):
    """Файловое хранилище формата XML на базе ElementTree."""

    def save(self, data: CinemaData, path: str | Path) -> None:
        target = Path(path)
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            root = ET.Element("online_cinema", attrib={"schema_version": "1.0"})
            for collection_name, records in data.to_dict().items():
                collection = ET.SubElement(root, collection_name)
                for record in records:
                    self._append_value(collection, "item", record)
            tree = ET.ElementTree(root)
            ET.indent(tree, space="    ")
            tree.write(target, encoding="utf-8", xml_declaration=True)
        except (OSError, TypeError, ValueError, ET.ParseError) as exc:
            raise StorageError(
                f"Не удалось сохранить XML-файл {target}: {exc}"
            ) from exc

    def load(self, path: str | Path) -> CinemaData:
        target = Path(path)
        try:
            root = ET.parse(target).getroot()
            if root.tag != "online_cinema":
                raise ValueError(
                    "Корневой элемент XML должен называться online_cinema."
                )
            payload: dict[str, Any] = {}
            for collection in root:
                payload[collection.tag] = [
                    self._element_to_value(item) for item in collection.findall("item")
                ]
            return CinemaData.from_dict(payload)
        except (OSError, ET.ParseError, TypeError, ValueError, KeyError) as exc:
            raise StorageError(
                f"Не удалось загрузить XML-файл {target}: {exc}"
            ) from exc

    @classmethod
    def _append_value(cls, parent: ET.Element, tag: str, value: Any) -> None:
        """Рекурсивно добавляет словари и списки в XML-дерево."""
        element = ET.SubElement(parent, tag)
        if isinstance(value, dict):
            for key, nested_value in value.items():
                cls._append_value(element, key, nested_value)
        elif isinstance(value, list):
            for nested_value in value:
                cls._append_value(element, "item", nested_value)
        elif value is not None:
            element.text = str(value)

    @classmethod
    def _element_to_value(cls, element: ET.Element) -> Any:
        """Преобразует XML-элемент в словарь, список или строковое значение."""
        children = list(element)
        if not children:
            return element.text or ""
        if all(child.tag == "item" for child in children):
            return [cls._element_to_value(child) for child in children]
        return {child.tag: cls._element_to_value(child) for child in children}
