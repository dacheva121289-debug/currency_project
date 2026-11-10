"""Домашнее задание: два курса обмена к одной целевой валюте."""

import json
import tkinter as tk
from tkinter import ttk, messagebox
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


# Код валюты -> её название в интерфейсе.
CURRENCIES = {
    "EUR": "Евро",
    "USD": "Американский доллар",
    "RUB": "Российский рубль",
    "GBP": "Британский фунт",
    "CNY": "Китайский юань",
    "KZT": "Казахстанский тенге",
    "JPY": "Японская иена",
    "CHF": "Швейцарский франк",
}

API_URL = "https://open.er-api.com/v6/latest/{}"


def get_rates(base_currency):
    """Запросить актуальные справочные курсы в JSON и вернуть словарь rates."""
    url = API_URL.format(base_currency)
    request = Request(url, headers={"User-Agent": "CurrencyHomework/1.0"})
    with urlopen(request, timeout=12) as response:
        data = json.load(response)  # Получаем JSON, а не текст или HTML.

    if data.get("result") != "success" or "rates" not in data:
        raise ValueError("Сервис не вернул курсы валют.")

    return data["rates"], data.get("time_last_update_utc", "")


def exchange():
    """Показать два курса относительно выбранной целевой валюты."""
    base1 = base_currency_var.get()
    base2 = second_base_currency_var.get()
    target = target_currency_var.get()

    exchange_button.config(state="disabled")
    result_var.set("Получаем данные...")
    window.update_idletasks()

    try:
        first_rates, updated = get_rates(base1)
        # Не запрашиваем повторно данные, если обе базовые валюты совпали.
        second_rates, _ = (first_rates, updated) if base2 == base1 else get_rates(base2)

        first_rate = first_rates[target]
        second_rate = second_rates[target]
        result_var.set(
            f"1 {base1} = {first_rate:.4f} {target}\n"
            f"1 {base2} = {second_rate:.4f} {target}"
        )
        status_var.set("Курсы получены. Источник: ExchangeRate-API.")
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, KeyError) as error:
        result_var.set("Не удалось получить курсы. Проверь интернет и попробуй снова.")
        status_var.set("Ошибка загрузки данных.")
        messagebox.showerror("Ошибка", f"Не удалось получить курсы валют.\n{error}")
    finally:
        exchange_button.config(state="normal")


def update_names(*_args):
    first_name_var.set(CURRENCIES[base_currency_var.get()])
    second_name_var.set(CURRENCIES[second_base_currency_var.get()])
    target_name_var.set(CURRENCIES[target_currency_var.get()])


window = tk.Tk()
window.title("Курсы обмена валют")
window.geometry("490x685")
window.resizable(False, False)
window.configure(bg="#f5f6fa")

base_currency_var = tk.StringVar(value="EUR")
second_base_currency_var = tk.StringVar(value="USD")
target_currency_var = tk.StringVar(value="RUB")
first_name_var = tk.StringVar()
second_name_var = tk.StringVar()
target_name_var = tk.StringVar()
result_var = tk.StringVar(value="Выбери валюты и нажми кнопку.")
status_var = tk.StringVar(value="Для обновления курсов нужен интернет.")

container = tk.Frame(window, bg="#f5f6fa")
container.pack(fill="both", expand=True, padx=28, pady=18)


def add_currency_selector(heading, variable, name_var):
    tk.Label(container, text=heading, bg="#f5f6fa", font=("Arial", 12, "bold")).pack(pady=(8, 12))
    selector = ttk.Combobox(
        container, textvariable=variable, values=list(CURRENCIES),
        state="readonly", width=23, font=("Arial", 11),
    )
    selector.pack()
    tk.Label(container, textvariable=name_var, bg="#f5f6fa", font=("Arial", 11)).pack(pady=(10, 20))
    return selector


add_currency_selector("Базовая валюта", base_currency_var, first_name_var)
add_currency_selector("Вторая базовая валюта", second_base_currency_var, second_name_var)
add_currency_selector("Целевая валюта", target_currency_var, target_name_var)

exchange_button = tk.Button(
    container, text="Получить курс обмена", command=exchange,
    font=("Arial", 11), bg="#e5ebff", padx=12, pady=8,
)
exchange_button.pack(pady=(5, 16))

result_label = tk.Label(
    container, textvariable=result_var, bg="#f5f6fa", fg="#173d79",
    font=("Arial", 12, "bold"), justify="center", wraplength=420,
)
result_label.pack(pady=5)

tk.Label(
    container, textvariable=status_var, bg="#f5f6fa", fg="#657080",
    font=("Arial", 9), wraplength=425,
).pack(side="bottom", pady=8)

for variable in (base_currency_var, second_base_currency_var, target_currency_var):
    variable.trace_add("write", update_names)
update_names()

window.mainloop()
