import json

ad = {
    "type": "sell",
    "amount": 100,
    "currency": "USDT",
    "price": 90,
    "fiat": "RUB"
}

with open("ad.json", "w") as file:
    json.dump(ad, file, indent=4)

print("Файл ad.json создан!")
