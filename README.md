# Лабораторная работа № 1. Онлайн-кинотеатр LUMEN

**Студент:** Богданов Даниил Алексеевич  
**Группа:** ИДБ-25-12  
**Дисциплина:** Прикладное программирование  
**Вариант:** 4  
**Тема:** ООП в Python. Обработка исключительных ситуаций. Форматы XML и JSON.

## О проекте

LUMEN — учебная программа, моделирующая работу онлайн-кинотеатра. В ней описаны пользователи, фильмы, жанры, тарифы, подписки, отзывы, история просмотров, избранное, платежи, промокоды и устройства.

Программа хранит данные в памяти во время работы. Полный набор данных можно сохранить в JSON или XML, а затем загрузить обратно. Консольное меню показывает основные операции на примере каталога фильмов.

## Возможности

- 11 классов предметной области.
- Создание, чтение, изменение и удаление всех 11 типов объектов через `CinemaService`.
- Проверка значений, уникальности и связей между объектами.
- Поиск фильмов по названию, описанию и режиссёру.
- Собственные исключения и обработка ожидаемых ошибок.
- Запись и чтение полного набора данных в JSON и XML.
- Консольное меню для работы с каталогом.
- Статический HTML/CSS/JavaScript-прототип интерфейса.
- Автоматические тесты для сервисной логики и файлового хранения.

## Структура проекта

```text
lr1_online_cinema/
├── data/
│   ├── online_cinema.json        # пример набора данных в JSON
│   └── online_cinema.xml         # тот же набор в XML
├── diagrams/
│   ├── class_diagram.puml        # исходник UML в PlantUML
│   ├── class_diagram.dot         # исходник Graphviz
│   └── class_diagram.png         # изображение диаграммы
├── docs/
│   ├── architecture.md           # краткое описание архитектуры
│   ├── defense_questions.md      # ответы на вопросы к защите
│   ├── PROJECT_EXPLANATION_RU.md # разбор папок, классов и логики
│   ├── ЛР1_Отчет_Вариант_4.docx  # редактируемый отчёт
│   └── ЛР1_Отчет_Вариант_4.pdf   # отчёт для просмотра и сдачи
├── prototypes/
│   ├── index.html                # разметка прототипа
│   ├── styles.css                # оформление прототипа
│   ├── app.js                    # поиск и фильтрация
│   ├── preview_home.png          # снимок главной страницы
│   └── preview_catalog.png       # снимок каталога
├── src/online_cinema/
│   ├── __init__.py               # интерфейс пакета
│   ├── __main__.py               # запуск python -m online_cinema
│   ├── cli.py                    # консольное меню
│   ├── exceptions.py             # собственные исключения
│   ├── models.py                 # классы предметной области
│   ├── repository.py             # хранение объектов и CRUD
│   ├── sample_data.py            # демонстрационные данные
│   ├── service.py                # правила работы и связи объектов
│   └── storage.py                # чтение и запись JSON/XML
├── tests/
│   ├── test_service.py           # тесты CRUD и бизнес-правил
│   └── test_storage.py           # тесты JSON и XML
├── SUBMISSION_GUIDE_RU.md      # установка, GitHub и сдача
├── .gitignore
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Используемые технологии

- Python 3.10 или новее.
- Стандартная библиотека Python: `dataclasses`, `datetime`, `enum`, `json`, `xml.etree.ElementTree`, `pathlib`, `typing` и другие встроенные модули.
- `pytest` — запуск автоматических тестов.
- PlantUML и Graphviz — исходники UML-диаграммы.
- HTML, CSS и JavaScript — статический прототип интерфейса.
- Git — контроль версий.

Для обычной работы приложения внешние Python-библиотеки не нужны. При установке проекта через `pip install -e .` используется `setuptools` как инструмент сборки (он указан в `pyproject.toml` и при необходимости устанавливается автоматически). Внешний пакет `pytest` нужен только для автоматических тестов.

## Установка и запуск в Windows

Откройте PowerShell в корневой папке проекта.

1. Проверьте версию Python:

```powershell
py --version
```

Нужен Python 3.10 или новее.

2. Создайте и активируйте виртуальное окружение:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Установите проект и пакет для тестов:

```powershell
python -m pip install --upgrade pip
python -m pip install -e .
python -m pip install -r requirements.txt
```

4. Запустите приложение:

```powershell
python -m online_cinema
```

Для выхода выберите пункт `0`.

Если PowerShell не разрешает активацию виртуального окружения, используйте его Python напрямую:

```powershell
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m online_cinema
```

## Проверка тестами

Из корневой папки проекта выполните:

```powershell
python -m pytest
```

На проверенной версии проекта ожидается результат `26 passed`.

## UML-диаграмма

Исходник диаграммы находится в `diagrams/class_diagram.puml`, альтернативный исходник — в `diagrams/class_diagram.dot`, изображение — в `diagrams/class_diagram.png`.

![UML-диаграмма классов](diagrams/class_diagram.png)

## Прототип интерфейса

Чтобы открыть макет, запустите в браузере `prototypes/index.html`. В нём показаны главная страница и каталог фильмов. Поиск и фильтрация демонстрационные, связь с Python-приложением отсутствует.

![Главная страница](prototypes/preview_home.png)

![Каталог фильмов](prototypes/preview_catalog.png)

## Пример использования классов

```python
from online_cinema.models import Genre, Movie
from online_cinema.sample_data import create_sample_service

service = create_sample_service()
service.create(Genre(4, "Комедия"))
service.create(
    Movie(
        id=4,
        title="Новый фильм",
        description="Описание фильма",
        release_year=2025,
        duration_minutes=100,
        age_rating="12+",
        genre_ids=[4],
    )
)

movie = service.get(Movie, 4)
print(movie.title)
```

## Документация

- `docs/PROJECT_EXPLANATION_RU.md` — назначение файлов и подробный разбор программы.
- `docs/architecture.md` — краткая схема взаимодействия модулей.
- `docs/defense_questions.md` — ответы на вопросы для защиты.
- `SUBMISSION_GUIDE_RU.md` — установка Python и Git, запуск тестов, публикация на GitHub и отправка в ЭОС.

## Ограничения учебной модели

Программа не подключается к реальному видеохостингу, платёжному сервису или серверной базе данных. Фильмы, пользователи, платежи и подписки представлены объектами Python. Данные хранятся в памяти и сохраняются в файлы JSON или XML. HTML-прототип не подключён к Python-приложению.
