import json
from pathlib import Path

import pytest

from online_cinema.exceptions import StorageError
from online_cinema.sample_data import build_sample_data
from online_cinema.storage import JsonStorage, XmlStorage


@pytest.mark.parametrize(
    "storage, suffix", [(JsonStorage(), "json"), (XmlStorage(), "xml")]
)
def test_storage_round_trip(tmp_path: Path, storage, suffix: str) -> None:
    source = build_sample_data()
    target = tmp_path / f"cinema.{suffix}"

    storage.save(source, target)
    restored = storage.load(target)

    assert restored.to_dict() == source.to_dict()


def test_json_file_is_human_readable_and_utf8(tmp_path: Path) -> None:
    target = tmp_path / "cinema.json"
    JsonStorage().save(build_sample_data(), target)
    text = target.read_text(encoding="utf-8")
    assert "Последний сигнал" in text
    assert "\\u041f" not in text
    assert isinstance(json.loads(text), dict)


def test_invalid_json_is_reported_as_storage_error(tmp_path: Path) -> None:
    target = tmp_path / "broken.json"
    target.write_text("{broken", encoding="utf-8")
    with pytest.raises(StorageError):
        JsonStorage().load(target)


def test_invalid_xml_is_reported_as_storage_error(tmp_path: Path) -> None:
    target = tmp_path / "broken.xml"
    target.write_text("<online_cinema>", encoding="utf-8")
    with pytest.raises(StorageError):
        XmlStorage().load(target)


@pytest.mark.parametrize(
    "storage, suffix", [(JsonStorage(), "json"), (XmlStorage(), "xml")]
)
def test_empty_lists_and_false_boolean_round_trip(
    tmp_path: Path, storage, suffix: str
) -> None:
    from online_cinema.models import CinemaData, Genre, Movie, User

    source = CinemaData(
        users=[User(1, "Тестовый пользователь", "test@example.com", False)],
        genres=[Genre(1, "Драма")],
        movies=[Movie(1, "Пустой список", "Описание", 2025, 90, "12+", [], cast=[])],
    )
    target = tmp_path / f"empty.{suffix}"
    storage.save(source, target)
    restored = storage.load(target)
    assert restored.to_dict() == source.to_dict()


def test_invalid_boolean_json_is_reported_as_storage_error(tmp_path: Path) -> None:
    payload = build_sample_data().to_dict()
    payload["users"][0]["is_active"] = "not-a-boolean"
    target = tmp_path / "invalid_boolean.json"
    target.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(StorageError):
        JsonStorage().load(target)
