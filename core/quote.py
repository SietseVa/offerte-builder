from dataclasses import dataclass
from typing import Any
import streamlit as st
from core.models import ProductDef, Customer
from core.pricing import calculate_price

@dataclass
class QuoteItem:
    product: ProductDef
    inputs: dict[str, Any]
    quantity: int = 1

    @property
    def unit_price(self) -> float:
        return calculate_price(self.product, self.inputs)

    @property
    def line_total(self) -> float:
        return self.unit_price * self.quantity


class QuoteSession:
    ITEMS_KEY  = "quote_items"
    CUSTOMER_KEY = "quote_customer"

    @classmethod
    def items(cls) -> list[QuoteItem]:
        if cls.ITEMS_KEY not in st.session_state:
            st.session_state[cls.ITEMS_KEY] = []
        return st.session_state[cls.ITEMS_KEY]

    @classmethod
    def customer(cls) -> Customer:
        if cls.CUSTOMER_KEY not in st.session_state:
            st.session_state[cls.CUSTOMER_KEY] = Customer()
        return st.session_state[cls.CUSTOMER_KEY]

    @classmethod
    def set_customer(cls, **fields) -> None:
        current = cls.customer().model_dump()
        current.update(fields)
        st.session_state[cls.CUSTOMER_KEY] = Customer(**current)


    @classmethod
    def add(cls, item: QuoteItem) -> None:
        cls.items().append(item)

    @classmethod
    def remove(cls, index: int) -> None:
        items = cls.items()
        if 0 <= index < len(items):
            items.pop(index)

    @classmethod
    def clear(cls) -> None:
        st.session_state[cls.ITEMS_KEY] = []

    @classmethod
    def subtotal(cls) -> float:
        return sum(item.line_total for item in cls.items())

    @classmethod
    def total(cls, discount: float = 0.0) -> float:
        return cls.subtotal() * (1 + discount / 100)