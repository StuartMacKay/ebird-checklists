import decimal
from typing import Any, Optional

from django.db.models import Model


def str2bool(value: Optional[str]) -> Optional[bool]:
    return bool(value) if value else None


def str2int(value: Optional[str]) -> Optional[int]:
    return int(value) if value else None


def str2decimal(value: Optional[str]) -> Optional[decimal.Decimal]:
    return decimal.Decimal(value) if value else None


def update_object(obj: Model, values: dict[str, Any]) -> Model:
    for key, value in values.items():
        setattr(obj, key, value)
    obj.save()
    return obj
