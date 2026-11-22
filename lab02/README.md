# Лабораторна робота №2. Аналіз товарів складу

Варіант 7. Мета — побудувати функціональний конвеєр з `map`, `filter`, композицією та окремою агрегацією через `reduce`.

У `core.py` конвеєр додає до копії запису `total = price × stock`, множить цю вартість на коефіцієнт для обраної категорії, відбирає товари зі `stock >= min_stock`, сортує за спаданням `total` і за зростанням `id` при рівності, а потім бере перші `top_n` записів. `reduce_stats` повертає кількість записів, суму та середнє за їхніми `total`. Для порожнього набору всі три значення нульові.

CLI в `app.py` читає JSON та друкує Top-N і його статистику. `lab2/main.py` дає той самий запуск у форматі з методички, `lab2/lab2.py` надає доступ до того ж ядра.

З каталогу `lab02` (Python 3.10+):

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
pytest -q
python app.py --top 2 --boost-category Електроніка --factor 1.1 --min-stock 1
python -m lab2.main --data lab2/sample_data.json --top 3
python -m black --check .
python -m ruff check .
python -m mypy .
```

Без параметрів береться приклад `lab2/sample_data.json`, категорія «Електроніка», коефіцієнт 1,1, залишок від 1 та Top-2. У цьому прикладі Top-2 містить товари з `id` 1 та 2, їхня сумарна вартість — 462, середня — 231. `--top 0` повертає порожній список.

З кореня репозиторію: `python -m lab02` і `pytest -q lab02`.
