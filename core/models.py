from pydantic import BaseModel
from typing import Any, Literal, Optional

class FieldDef(BaseModel):
    id: str
    name: str
    type: Literal["number", "integer", "checkbox", "select", "text"]
    default: Any = None
    required: bool = True
    options: Optional[list[str]] = None
    visible_when: Optional[dict] = None
    min: Optional[float] = None
    max: Optional[float] = None

class PricingDef(BaseModel):
    formula: str
    variables: dict[str, float] = {}

class ProductDef(BaseModel):
    id: str
    name: str
    unit: str
    fields: list[FieldDef]
    pricing: PricingDef

class Catalog(BaseModel):
    products: dict[str, list[ProductDef]]

class Customer(BaseModel):
    name: str = ""
    address: str = ""
    email: str = ""
    phone: str = ""
    