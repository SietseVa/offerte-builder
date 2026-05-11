import yaml
from pathlib import Path
from core.models import Catalog, ProductDef

def load_catalog(path: str | Path = "data/products.yaml") -> Catalog:
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return Catalog(**raw)

def find_product(catalog: Catalog, product_id: str) -> tuple[str, ProductDef] | tuple[None, None]:
    for category, products in catalog.products.items():
        for product in products:
            if product.id == product_id:
                return category, product
    return None, None