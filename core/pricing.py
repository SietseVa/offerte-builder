def calculate_price(product, user_inputs: dict) -> float:
    namespace = {**product.pricing.variables, **user_inputs}
    return eval(product.pricing.formula, {"__builtins__": {}}, namespace)
