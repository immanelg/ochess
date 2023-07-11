from typing import Any, Type, TypeAlias

from pydantic import BaseModel

Data: TypeAlias = dict[str, Any]


def validated_json(data: Data, schema: Type[BaseModel]) -> Data:
    """Validates dict and returns it normalized."""
    return schema.model_validate(data).model_dump()
