"""Текстовый интерфейс приложения онлайн-кинотеатра."""

from pathlib import Path

from .exceptions import CinemaError
from .models import Genre, Movie
from .sample_data import create_sample_service
from .service import CinemaService
from .storage import JsonStorage, XmlStorage


DATA_DIR = Path(__file__).resolve().parents[2] / "data"
JSON_PATH = DATA_DIR / "online_cinema.json"
XML_PATH = DATA_DIR / "online_cinema.xml"


def _print_movies(service: CinemaService) -> None:
    movies = service.get_all(Movie)
    if not movies:
        print("Каталог пуст.")
        return
    for movie in movies:
        print(
            f"[{movie.id}] {movie.title} ({movie.release_year}), "
            f"{movie.duration_minutes} мин., {movie.age_rating}"
        )


def main() -> None:
    """Запускает меню и перехватывает ожидаемые ошибки пользовательского ввода."""
    service = create_sample_service()
    json_storage = JsonStorage()
    xml_storage = XmlStorage()

    while True:
        print("\n=== LUMEN | Онлайн-кинотеатр ===")
        print("1. Показать каталог")
        print("2. Найти фильм")
        print("3. Добавить фильм")
        print("4. Изменить описание фильма")
        print("5. Удалить фильм")
        print("6. Сохранить данные в JSON")
        print("7. Сохранить данные в XML")
        print("8. Загрузить данные из JSON")
        print("9. Загрузить данные из XML")
        print("0. Выход")

        try:
            choice = input("Выберите действие: ").strip()
            if choice == "1":
                _print_movies(service)
            elif choice == "2":
                query = input("Название, описание или режиссер: ")
                for movie in service.search_movies(query):
                    print(f"[{movie.id}] {movie.title} ({movie.release_year})")
            elif choice == "3":
                movie = Movie(
                    id=int(input("ID фильма: ")),
                    title=input("Название: ").strip(),
                    description=input("Описание: ").strip(),
                    release_year=int(input("Год выпуска: ")),
                    duration_minutes=int(input("Длительность в минутах: ")),
                    age_rating=input(
                        "Возрастной рейтинг (0+/6+/12+/16+/18+): "
                    ).strip(),
                    genre_ids=[
                        int(value)
                        for value in input("ID жанров через запятую: ").split(",")
                        if value.strip()
                    ],
                    director=input("Режиссер: ").strip() or "Не указан",
                )
                service.create(movie)
                print("Фильм добавлен.")
            elif choice == "4":
                movie_id = int(input("ID фильма: "))
                description = input("Новое описание: ").strip()
                service.update(Movie, movie_id, description=description)
                print("Описание обновлено.")
            elif choice == "5":
                movie_id = int(input("ID фильма: "))
                service.delete(Movie, movie_id)
                print("Фильм удален.")
            elif choice == "6":
                json_storage.save(service.export_data(), JSON_PATH)
                print(f"Данные сохранены: {JSON_PATH}")
            elif choice == "7":
                xml_storage.save(service.export_data(), XML_PATH)
                print(f"Данные сохранены: {XML_PATH}")
            elif choice == "8":
                service.import_data(json_storage.load(JSON_PATH))
                print("Данные загружены из JSON.")
            elif choice == "9":
                service.import_data(xml_storage.load(XML_PATH))
                print("Данные загружены из XML.")
            elif choice == "0":
                print("Работа завершена.")
                break
            else:
                print("Неизвестная команда. Выберите пункт от 0 до 9.")
        except (CinemaError, ValueError, TypeError) as exc:
            # Ошибка выводится пользователю, но не завершает главный цикл приложения.
            print(f"Ошибка: {exc}")
        except (EOFError, KeyboardInterrupt):
            print("\nРабота завершена пользователем.")
            break
