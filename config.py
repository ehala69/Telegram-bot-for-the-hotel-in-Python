# Константы
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SUPERGROUP_ID = os.getenv("SUPERGROUP_ID")

# Данные о номерах
ROOM_DATA = {
    "01": {
        "photos": [
            "AgACAgIAAxkBAAIoZGeWRdz0rU-xxAUtJ6Nd0VHkXH7YAAJh8TEbQ5qxSIdU8cqJG7nWAQADAgADeQADNgQ",
            "AgACAgIAAxkBAAIoZmeWRhW9PSVZNpnfSNLcubbYhV8FAAJk8TEbQ5qxSOHgDq_kYgHYAQADAgADeQADNgQ",
            "AgACAgIAAxkBAAIoaGeWRj5Zb0ETdoYsNav77VKD-xWvAAJl8TEbQ5qxSHGXjsiIYKDBAQADAgADeQADNgQ"
        ],
        "description": "Номер: 01\nЦена: 25000тг\nСтатус: Номер свободен ✅"
    },
    "02": {
        "photos": [
            "AgACAgIAAxkBAAIppWeYrzTpAVUd4RE8ULjIMRHsFV8-AAKJ6jEbmzDISBUzVta-rnWjAQADAgADeQADNgQ",
            "AgACAgIAAxkBAAIpp2eYr0tHxhSPvJs1vO8FO7BflqUrAAKK6jEbmzDISDUMZajOe7NLAQADAgADeQADNgQ",
            "AgACAgIAAxkBAAIpqWeYr1WpN0I0_3DRO9Rkgr3E5JKgAAKL6jEbmzDISKJcHUc7_7tEAQADAgADeQADNgQ"
        ],
        "description": "Номер: 02\nЦена: 25000тг\nСтатус: Номер свободен ✅"
    },
    "03": {
        "photos": [
            "AgACAgIAAxkBAAIpq2eYr2JG41nUtpGCHLA3bWrvgbS-AAKM6jEbmzDISM-0MRQe0tifAQADAgADeQADNgQ",
            "AgACAgIAAxkBAAIprWeYr2wo9h5Cbktf3bgLg2v_HdcuAAKO6jEbmzDISDRPMNN9gANEAQADAgADeQADNgQ",
            "AgACAgIAAxkBAAIpr2eYr3waQnIlipHlIeRRENzK2rGDAAKR6jEbmzDISKx4rgW8XbMyAQADAgADeQADNgQ"
        ],
        "description": "Номер: 03\nЦена: 25000тг\nСтатус: Номер свободен ✅"
    },
    "04": {
        "photos": [
            "AgACAgIAAxkBAAIpr2eYr3waQnIlipHlIeRRENzK2rGDAAKR6jEbmzDISKx4rgW8XbMyAQADAgADeQADNgQ",
            "AgACAgIAAxkBAAIps2eYr6U5_WDDDRUOBkt6SqdyS43mAAKT6jEbmzDISMqiZ71qOz05AQADAgADeQADNgQ",
            "AgACAgIAAxkBAAIptWeYr7FxUwbTSstSHKkIE8KdDdqTAAKU6jEbmzDISJUjVGCJc29uAQADAgADeQADNgQ"
        ],
        "description": "Номер: 04\nЦена: 30000тг\nСтатус: Номер свободен ✅"
    },
    "05": {
        "photos": [
            "AgACAgIAAxkBAAIpt2eYr73P4jM3PiYHGT8DkGmhZN6KAAKV6jEbmzDISOLda5vTbmn-AQADAgADeQADNgQ",
            "AgACAgIAAxkBAAIpuWeYr8xRWzkG97LW2bb93RJXDJ2SAAKW6jEbmzDISE33OGv66z1_AQADAgADeQADNgQ",
            "AgACAgIAAxkBAAIpu2eYr90uXc1qVIdb5tkUIVoAARWfyAACmOoxG5swyEj5ozl6e0-5IgEAAwIAA3kAAzYE"
        ],
        "description": "Номер: 05\nЦена: 30000тг\nСтатус: Номер свободен ✅"
    },
    "06": {
        "photos": [
            "AgACAgIAAxkBAAIpvWeYr-1Ftx10F1poAt_XxguBXPc4AAKa6jEbmzDISBb2-VqFhzjuAQADAgADeQADNgQ",
            "AgACAgIAAxkBAAIpv2eYr_r5TIxdmcAYGe7fRtJO-lC-AAKb6jEbmzDISN2NfuSw9EQXAQADAgADeQADNgQ",
            "AgACAgIAAxkBAAIpwWeYsBm2XlAk9w-9OpVzuv3ZfJPsAAKd6jEbmzDISJzNX1XG8szVAQADAgADeQADNgQ"
        ],
        "description": "Номер: 06\nЦена: 30000тг\nСтатус: Номер свободен ✅"
    },
    "07": {
        "photos": [
            "AgACAgIAAxkBAAIpw2eYsCaaqLz6Z-ztTzO9uIDN_psTAAKe6jEbmzDISLHMenW4xT8EAQADAgADeQADNgQ",
            "AgACAgIAAxkBAAIpxWeYsC85F5OtBV_ihuC68d3jtTJHAAKf6jEbmzDISJOc4Y8gFaCTAQADAgADeQADNgQ",
            "AgACAgIAAxkBAAIpx2eYsDxwCimFFH3UiVLs4LuAUA9xAAKg6jEbmzDISD3GRQ6BpakPAQADAgADeQADNgQ"
        ],
        "description": "Номер: 07\nЦена: 40000тг\nСтатус: Номер свободен ✅"
    },
    "08": {
        "photos": [
            "AgACAgIAAxkBAAIpymeYsKzqk1p0H61jqM9e25lruwwGAAKi6jEbmzDISDpEcnCUT7cyAQADAgADeQADNgQ",
            "AgACAgIAAxkBAAIpzGeYsLVvhREznA4P6I9Z-07swboeAAKj6jEbmzDISDTEA-A1x6wXAQADAgADeQADNgQ",
            "AgACAgIAAxkBAAIp0GeYsNUNiXxJlUP_EWbQm1M0spgyAAKl6jEbmzDISGK8v3rvv2tuAQADAgADeQADNgQ"
        ],
        "description": "Номер: 08\nЦена: 40000тг\nСтатус: Номер свободен ✅"
    },
    "09": {
            "photos": [
            "AgACAgIAAxkBAAIp0meYsOMxizs4pbGz-uk7hUBkDSksAAKn6jEbmzDISI1Uo5ISipvIAQADAgADeQADNgQ",
            "AgACAgIAAxkBAAIp1GeYsPpC_VjfZM_4Cnz0bq23CBIpAAKo6jEbmzDISHKmZF0sAAGQQQEAAwIAA3kAAzYE",
            "AgACAgIAAxkBAAIp1meYsQQw3OlcD6PK2LKDJE4G0MUHAAKp6jEbmzDISDYJFM-IFUWlAQADAgADeQADNgQ"
        ],
            "description": "Номер: 09\nЦена: 40000тг\nСтатус: Номер свободен ✅"
    },
    "10": {
            "photos": [
            "AgACAgIAAxkBAAIp2GeYsQ-rrVQlvCBrMdJaDlvw8hqTAAKq6jEbmzDISB0WtEOha-YhAQADAgADeQADNgQ",
            "AgACAgIAAxkBAAIp2meYsSqrFZFZZh6lVgmca-olz69LAAKr6jEbmzDISKtGP_6-XBriAQADAgADeQADNgQ",
            "AgACAgIAAxkBAAIp3GeYsTXTu4Uo0FQNhcWAeVbjSDr-AAKs6jEbmzDISNI8NDCCCv36AQADAgADeQADNgQ"
        ],
            "description": "Номер: 10\nЦена: 40000тг\nСтатус: Номер свободен ✅"
    },
    "11": {
            "photos": [
            "AgACAgIAAxkBAAIp3meYsULMKTq8NqsrooxJt3ao2bx7AAKt6jEbmzDISHgpdXVjOqsIAQADAgADeQADNgQ",
            "AgACAgIAAxkBAAIp4GeYsU-djc-1FIqwq4bE2Gk9Rd9JAAKu6jEbmzDISF6HQOXJC0VtAQADAgADeQADNgQ",
            "AgACAgIAAxkBAAIp4meYsVs-dmVjutoVByLUdx81E40QAAKv6jEbmzDISF1xyL21nXCaAQADAgADeQADNgQ"
        ],
            "description": "Номер: 11\nЦена: 40000тг\nСтатус: Номер свободен ✅"
    },
    "12": {
            "photos": [
            "AgACAgIAAxkBAAIp5GeYsWevPn1wWYwLNFg2IOp0DCQYAAKw6jEbmzDISDF2YamjRqRoAQADAgADeQADNgQ",
            "AgACAgIAAxkBAAIp5meYsXgwuqPYSc_GOjzsvkyv1MkpAAKx6jEbmzDISDnr6J652EFbAQADAgADeQADNgQ",
            "AgACAgIAAxkBAAIp6GeYsYhUJPG59FbXgtbi10QnmmJ9AAKy6jEbmzDISCg0MeIRz3LIAQADAgADeQADNgQ"
        ],
            "description": "Номер: 12\nЦена: 40000тг\nСтатус: Номер свободен ✅"
    },
    "13": {
            "photos": [
            "AgACAgIAAxkBAAIp62eYsfXULqSUVobe5Kj3XaOSB4wOAAK06jEbmzDISHv4Su4QgkwtAQADAgADeQADNgQ",
            "AgACAgIAAxkBAAIp7WeYsgQ9UbodrC2vcALegcKjpTYqAAK16jEbmzDISJD5m-ASXKzJAQADAgADeQADNgQ",
            "AgACAgIAAxkBAAIp72eYsiUow4b6smQAAQEiMjF9h2JQzAACtuoxG5swyEjUHVoDH-4IHAEAAwIAA3kAAzYE"
        ],
            "description": "Номер: 13\nЦена: 40000тг\nСтатус: Номер свободен ✅"
    }
}

CATEGORY_DATA = {
    "standard": {"name": "Стандарт", "price": "25000тг", "rooms": ["01", "02", "03"]},
    "pollux": {"name": "Полулюкс", "price": "30000тг", "rooms": ["04", "05", "06", "07", "08", "09"]},
    "luxe": {"name": "Люкс", "price": "40000тг", "rooms": ["10", "11", "12", "13"]},
}