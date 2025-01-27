import datetime as dt
import decimal
from typing import Any, Optional

from django.db.models import Model
from django.utils.timezone import get_default_timezone


def str2bool(value: Optional[str]) -> Optional[bool]:
    return bool(value) if value else None


def str2int(value: Optional[str]) -> Optional[int]:
    return int(value) if value else None


def float2int(value: Optional[float]) -> Optional[int]:
    return int(value) if value else None


def str2decimal(value: Optional[str]) -> Optional[decimal.Decimal]:
    return decimal.Decimal(value) if value else None


def str2datetime(value: str) -> dt.datetime:
    return dt.datetime.fromisoformat(value).replace(tzinfo=get_default_timezone())


def str2date(value: str) -> dt.date:
    return str2datetime(value).date()


def update_object(obj: Model, values: dict[str, Any]) -> Model:
    for key, value in values.items():
        setattr(obj, key, value)
    obj.save()
    return obj
