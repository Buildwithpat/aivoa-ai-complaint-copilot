from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    """Base schema that serializes snake_case fields as camelCase JSON,
    matching the frontend's AI JSON contract (see PROJECT_CONTEXT.md and
    client/src/types/complaint.types.ts) while keeping snake_case attribute
    names on the Python side for direct use with SQLAlchemy models."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )
