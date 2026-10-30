import pytest

from online_cinema.exceptions import (
    BusinessRuleError,
    DuplicateEntityError,
    EntityNotFoundError,
    ValidationError,
)
from online_cinema.models import (
    Genre,
    Movie,
    Review,
    Subscription,
    SubscriptionPlan,
    User,
)
from online_cinema.sample_data import create_sample_service
from online_cinema.service import CinemaService


def test_create_read_update_delete_movie() -> None:
    service = CinemaService()
    service.create(Genre(1, "Драма"))
    movie = Movie(1, "Тестовый фильм", "Описание", 2025, 100, "12+", [1])

    service.create(movie)
    assert service.get(Movie, 1).title == "Тестовый фильм"

    service.update(Movie, 1, title="Новое название")
    assert service.get(Movie, 1).title == "Новое название"

    service.delete(Movie, 1)
    with pytest.raises(EntityNotFoundError):
        service.get(Movie, 1)


def test_duplicate_user_email_is_rejected() -> None:
    service = CinemaService()
    service.create(User(1, "Первый пользователь", "same@example.com"))
    with pytest.raises(DuplicateEntityError):
        service.create(User(2, "Второй пользователь", "SAME@example.com"))


def test_duplicate_id_is_rejected() -> None:
    service = CinemaService()
    service.create(User(1, "Пользователь", "user@example.com"))
    with pytest.raises(DuplicateEntityError):
        service.create(User(1, "Другой пользователь", "other@example.com"))


def test_invalid_movie_age_rating_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Movie(1, "Фильм", "Описание", 2024, 90, "21+")


def test_movie_requires_existing_genre() -> None:
    service = CinemaService()
    with pytest.raises(EntityNotFoundError):
        service.create(Movie(1, "Фильм", "Описание", 2024, 90, "12+", [999]))


def test_genre_cannot_be_deleted_while_used() -> None:
    service = create_sample_service()
    with pytest.raises(BusinessRuleError):
        service.delete(Genre, 1)


def test_review_requires_existing_user_and_movie() -> None:
    service = CinemaService()
    with pytest.raises(EntityNotFoundError):
        service.create(Review(1, 10, 20, 8))


def test_user_email_is_normalised() -> None:
    user = User(1, "Пользователь", " TEST@Example.com ")
    assert user.email == "test@example.com"


def test_search_movies_finds_title_and_director() -> None:
    service = create_sample_service()
    assert len(service.search_movies("последний")) == 1
    assert len(service.search_movies("миронова")) == 1
    assert service.search_movies("несуществующее") == []


def test_import_data_replaces_service_state() -> None:
    first = create_sample_service()
    second = CinemaService()
    second.import_data(first.export_data())
    assert second.export_data().to_dict() == first.export_data().to_dict()


def test_subscription_owner_cannot_change_when_payment_exists() -> None:
    service = create_sample_service()
    with pytest.raises(BusinessRuleError):
        service.update(Subscription, 1, user_id=2)



@pytest.mark.parametrize("rating", [7.5, True])
def test_review_rating_must_be_an_integer(rating: int | float) -> None:
    with pytest.raises(ValidationError):
        Review(1, 1, 1, rating)


@pytest.mark.parametrize("entity_id", [True, 1.5])
def test_identifier_must_be_an_integer(entity_id: int | float) -> None:
    with pytest.raises(ValidationError):
        Genre(entity_id, "Драма")


@pytest.mark.parametrize("price", [float("nan"), float("inf"), True])
def test_subscription_plan_rejects_invalid_price(price: int | float) -> None:
    with pytest.raises(ValidationError):
        SubscriptionPlan(1, "Стандарт", price, 30, 2)
