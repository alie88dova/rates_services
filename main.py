from typing import List, Dict

import uvicorn
import json
from datetime import datetime, date
from fastapi import FastAPI
from pydantic import BaseModel
from tortoise.contrib.fastapi import register_tortoise

from models import Cargo

RATES_JSON = "rates.json"

class CargoItem(BaseModel):
    cargo_type: str
    rate: float


class CargoData(BaseModel):
    date: str
    rates: List[CargoItem]


def get_json() -> dict:
    with open(RATES_JSON, "r") as f:
        costs = json.loads(f.read())
        return costs


def get_rate(date: str, cargo_type) -> float:
    c = get_json()
    rate = 0
    for i in c[f"{date}"]:
        print(i)
        print(cargo_type)
        if i["cargo_type"] == cargo_type:
            return float(i["rate"])
        if i["cargo_type"] == "Other":
            rate = float(i["rate"])
    return rate


app = FastAPI(
    title="Расчет стоимости страхования"
)


@app.get("/get_cost")
async def get_cost(
        date: str,
        price: float,
        cargo_type: str
):
    try:
        print(date)
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        rate = get_rate(date, cargo_type)
        cargo_price = price * rate
        await Cargo.create(
            date=date,
            type=cargo_type,
            rate=rate,
            start_cost=price,
            add_cost = cargo_price
        )
        return {
            "price": cargo_price
        }
    except ValueError as e:
        return {
            "error": f"Invalid date format. Please use format YYYY-MM-DD.\n {e}"
        }
    except KeyError:
        return {
            "error": f"Цены для {date} не созданы"
        }


async def check_correct_data(data: list):
    rates = [dict(x) for x in data]
    correct = False
    for rate in rates:
        if rate["cargo_type"] == "Other":
            correct = True
    if not correct:
        raise ValueError("Отсутствует Other")


@app.post("/add_new_rate")
async def add_rate(data: List[CargoData]):
    try:
        cur_rates = get_json()
        for rd in data:
            # Для проверки корректности даты
            date_obj = datetime.strptime(rd.date, "%Y-%m-%d").date()

            if rd.date in list(cur_rates.keys()):
                return {
                    "status": "error",
                    "data": f"Это дата {rd.date} существует"
                }

        for rd in data:
            await check_correct_data(rd.rates)
            cur_rates[rd.date] = [dict(x) for x in rd.rates]

        with open(RATES_JSON, "w+") as f:
            f.write(json.dumps(cur_rates))

        return {
            "status": "correct"
        }
    except ValueError as e:
        return {
            "error": f"Invalid date format. Please use format YYYY-MM-DD.\n {e}"
        }


register_tortoise(
    app,
    db_url="postgres://root:fynbgjdbdfy@31.129.97.89:5432/cargo_db",
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
