import streamlit as st
from core.quote import QuoteSession

def render_customer_form():
    customer = QuoteSession.customer()

    col1, col2 = st.columns(2)
    name = col1.text_input("Naam / bedrijfsnaam", value=customer.name)
    email = col2.text_input("E-mailadres", value=customer.email)

    col3, col4 = st.columns(2)
    phone = col3.text_input("Telefoonnummer", value=customer.phone)
    address = col4.text_area("Adres", value=customer.address, height=80)

    QuoteSession.set_customer(
        name=name,
        email=email,
        phone=phone,
        address=address,
    )

def render_quote(discount: float = 0.0, visible: bool = True):
    items = QuoteSession.items()
    if not items:
        st.info("Nog geen producten toegevoegd aan de offerte.")
        return

    for i, item in enumerate(items):
        with st.container(border=True):
            cols = st.columns([5, 2, 2, 1, 1])
            cols[0].markdown(f"**{item.product.name}**")
            cols[1].write(f"€ {item.unit_price:,.2f}")
            cols[2].write(f"× {item.quantity}")
            cols[3].write(f"€ {item.line_total:,.2f}")
            if cols[4].button("🗑️", key=f"remove_{i}", help="Verwijder dit item"):
                QuoteSession.remove(i)
                st.rerun()

    subtotal = sum(item.line_total for item in items)
    adjustment = subtotal * discount / 100
    if visible and discount != 0:
        st.divider()
        cols = st.columns([4, 1, 1, 1])
        label = "Korting" if discount < 0 else "Meerprijs"
        cols[0].markdown(f"**{label}**")
        cols[1].write("")
        cols[2].write(f"{discount:,.1f} %")
        cols[3].write(f"€ {adjustment:,.2f}")
    

    vat = (subtotal + adjustment) * 0.21
    total_with_vat = subtotal + adjustment + vat

    st.divider()
    cols = st.columns([4, 1, 1, 1])
    label = "BTW (21%)"
    cols[0].markdown(f"**{label}**")
    cols[1].write("")
    cols[2].write("")
    cols[3].write(f"€ {vat:,.2f}")

    st.markdown(f"### Totaal: € {total_with_vat:,.2f}")