import streamlit as st

def render_fields(product, key_prefix: str = "") -> dict:
    """Renders input widgets for a product and returns user values."""
    values = {}

    for field in product.fields:
        widget_key = f"{key_prefix}_{product.id}_{field.id}"
        # Handle conditional visibility
        if field.visible_when:
            trigger = field.visible_when["field"]
            if values.get(trigger) != field.visible_when["value"]:
                continue

        if field.type == "number":
            values[field.id] = st.number_input(
                field.name,
                min_value=float(field.min or 0),
                max_value=float(field.max) if field.max else None,
                value=float(field.default or field.min or 0),
                step=0.1,
                key=widget_key,
            )
        elif field.type == "integer":
            values[field.id] = st.number_input(
                field.name,
                min_value=int(field.min or 1),
                value=int(field.default or 1),
                step=1,
                key=widget_key,
            )
        elif field.type == "checkbox":
            values[field.id] = st.checkbox(
                field.name,
                value=bool(field.default),
                key=widget_key,
            )
        elif field.type == "select":
            values[field.id] = st.selectbox(
                field.name,
                options=field.options,
                index=field.options.index(field.default) if field.default else 0,
                key=widget_key,
            )

    return values
