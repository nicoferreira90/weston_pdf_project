"""Selected fields and the result contract shared with the API."""

from enum import StrEnum
from typing import Literal, Self

from pydantic import BaseModel, model_validator


class FieldId(StrEnum):
    PURCHASER_NAME = "purchaser_name"
    PURCHASE_PRICE = "purchase_price"
    CONTRACT_DATE = "contract_date"
    PROPERTY_ADDRESS = "property_address"


class ExtractionResult(BaseModel):
    field_id: FieldId
    status: Literal["found", "missing"]
    value: str | None

    @model_validator(mode="after")
    def validate_status_and_value(self) -> Self:
        if self.status == "found" and (self.value is None or not self.value.strip()):
            raise ValueError("A found field requires a nonempty value.")
        if self.status == "missing" and self.value is not None:
            raise ValueError("A missing field requires a null value.")
        return self


class ExtractionResponse(BaseModel):
    results: list[ExtractionResult]
