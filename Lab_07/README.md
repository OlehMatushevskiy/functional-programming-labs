# Лабораторна №7. functools та operator

Варіант 7. Готельні бронювання.

- `loaders.py` містить `load_bookings` на `singledispatch`. Функція приймає JSON або CSV як текст, шлях як `str` або `Path`, відкритий текстовий файл чи готовий список словників. Зовнішній файл читається з поточної позиції й залишається відкритим. Значення, прочитані з CSV, на етапі завантаження мають тип `str`.
- `lab07.py` містить `pipeline(value, *funcs)` на `reduce` і `clean_and_rank(path_or_str, top=3, *, tariffs=None)`. Конвеєр завантажує бронювання, нормалізує поля, відбирає записи зі статусом `confirmed` і повертає до `top` записів. Сортування йде за спаданням `total_price`, за рівної суми — за зростанням імені гостя.
- `models.py` містить `Booking` із `total_ordering`. Природний порядок починається із загальної вартості за зростанням, а за рівної вартості враховує ім’я гостя, тип номера та решту полів.
- `main.py` запускає демонстрацію на `sample_data.json` і коротку самоперевірку, якщо `RUN_TESTS = True`.

`price` — ціна за ніч. `total_price = nights * price * rate`. Коефіцієнт за замовчуванням дорівнює 1. Наприклад, `tariffs={"suite": 1.25}` застосовує коефіцієнт 1,25 до номерів типу `suite`. `partial` фіксує тарифи для нормалізації та налаштовує етапи `map`, `filter` і `sorted`. `itemgetter` дістає поля, а `methodcaller` викликає рядкові методи.

Для запуску потрібен Python 3.10 або новіший. З кореня репозиторію виконай `python3 Lab_07/main.py`.

```bash
cd Lab_07
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
python -m pytest -q
python -m mypy .
python -m black --check .
python -m ruff check .
```

Демо повертає Bob (4500.00), Alice (3000.00) і Dan (3000.00). Carol зі статусом `pending` відфільтрована, Eva має нижчу вартість.
