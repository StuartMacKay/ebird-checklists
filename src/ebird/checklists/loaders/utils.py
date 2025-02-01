import datetime as dt
import decimal
import random
import string

from django.utils.timezone import get_default_timezone


def str2bool(value: str | None) -> bool | None:
    return bool(value) if value else None


def str2int(value: str | None) -> int | None:
    return int(value) if value else None


def float2int(value: float | None) -> int | None:
    return int(value) if value else None


def str2decimal(value: str | None) -> decimal.Decimal | None:
    return decimal.Decimal(value) if value else None


def str2datetime(value: str) -> dt.datetime:
    return dt.datetime.fromisoformat(value).replace(tzinfo=get_default_timezone())


def str2date(value: str) -> dt.date:
    return str2datetime(value).date()


def random_code(length: int, prefix: str = ""):
    return prefix + "".join(random.choices(string.digits, k=length))
