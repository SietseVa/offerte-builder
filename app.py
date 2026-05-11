import streamlit as st
from core.catalog import load_catalog
from core.pricing import calculate_price
from core.quote import QuoteSession, QuoteItem
from ui.field_renderer import render_fields
from ui.quote_view import render_quote, render_customer_form
from core.export import build_quote_pdf

st.set_page_config(page_title="Schaverij Hattem", layout="wide")

@st.cache_resource
def get_catalog():
    return load_catalog()

catalog = get_catalog()

st.title("Schaverij Hattem - Offerte Builder")

with st.expander("Klantgegevens", expanded=not QuoteSession.customer().name):
    render_customer_form()

left, right = st.columns([1, 1])

with left:
    st.header("Product toevoegen")

    categories = list(catalog.products.keys())
    category = st.selectbox("Categorie", categories)

    products = catalog.products[category]
    product_lookup = {p.name: p for p in products}
    product_name = st.selectbox("Product", list(product_lookup.keys()))
    product = product_lookup[product_name]

    st.caption(f"Eenheid: {product.unit}")

    inputs = render_fields(product, key_prefix="builder")
    quantity = st.number_input("Aantal", min_value=1, value=1, step=1, key="builder_qty")

    unit_price = None
    try:
        unit_price = calculate_price(product, inputs)
    except Exception as e:
        st.warning(f"Prijs nog niet te berekenen: {e}")

    if unit_price is not None:
        c1, c2 = st.columns(2)
        c1.metric("Stukprijs", f"€ {unit_price:,.2f}")
        c2.metric("Regeltotaal", f"€ {unit_price * quantity:,.2f}")

    if st.button("Toevoegen aan offerte", type="primary", disabled=unit_price is None):
        QuoteSession.add(QuoteItem(product=product, inputs=dict(inputs), quantity=int(quantity)))
        st.rerun()

with right:
    st.header("Offerte")
    with st.expander("Extra opties"):
        c1, c2 = st.columns(2)
        with c1:
            discount = st.number_input(
                "Korting (-) of meerprijs (+) (%)",
                min_value=-100.0,
                max_value=100.0,
                value=0.0,
                step=1.0,
                key="quote_discount",
            )
            zichtbaar_checked = discount <= 0
        with c2:
            st.write("")
            st.write("")
            zichtbaar = st.checkbox("Zichtbaar voor klant", value=zichtbaar_checked, key="quote_visible")

    render_quote(discount=discount, visible=zichtbaar)

    if QuoteSession.items():
        customer = QuoteSession.customer()
        filename_base = customer.name.strip().replace(" ", "_") or "offerte"
        pdf_bytes = build_quote_pdf(
            customer,
            QuoteSession.items(),
            discount=discount,
            visible=zichtbaar,
        )

        col_a, col_b = st.columns(2)
        col_a.download_button(
            label="Download offerte (PDF)",
            data=pdf_bytes,
            file_name=f"offerte_{filename_base}.pdf",
            mime="application/pdf",
            type="primary",
        )
    
    if QuoteSession.items():
        if st.button("Offerte leegmaken"):
            QuoteSession.clear()
            st.rerun()