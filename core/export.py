from io import BytesIO
from datetime import date
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
)
from reportlab.pdfgen import canvas
from core.models import Customer
from core.quote import QuoteItem


def _format_inputs(product, inputs: dict) -> str:
    label_map = {field.id: field.name for field in product.fields}
    specs = []
    for field in product.fields:
        if field.id in inputs:
            value = inputs[field.id]
            if isinstance(value, bool):
                value = "Ja" if value else "Nee"
            specs.append(f"{field.name}: {value}")
    return ", ".join(specs)


def _eur(value: float) -> str:
    return f"€ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def build_quote_pdf(customer: Customer, items: list[QuoteItem], discount: float = 0.0, visible: bool = True) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2.5 * cm,
        title="Offerte",
    )

    styles = getSampleStyleSheet()
    h1 = styles["Heading1"]
    h2 = styles["Heading2"]
    body = styles["BodyText"]
    small = ParagraphStyle("small", parent=body, fontSize=8, textColor=colors.grey, leading=10)
    company_style = ParagraphStyle("company", parent=body, fontSize=9, leading=12)

    story = []

    header_data = [
        [
            _build_customer_info_table(customer, body),
            _build_company_header(company_style)
        ]
    ]
    header_table = Table(header_data, colWidths=[10 * cm, 6 * cm])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (0, 0), (0, 0), "LEFT"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 1 * cm))

    story.append(Paragraph("Offerte", h1))
    story.append(Paragraph(f"Datum: {date.today().strftime('%d-%m-%Y')}", body))
    story.append(Spacer(1, 0.8 * cm))

    story.append(Paragraph("Producten", h2))
    story.append(Spacer(1, 0.3 * cm))

    header = ["Product", "Specificatie", "Aantal", "Stukprijs", "Regeltotaal"]
    rows = [header]
    for item in items:
        product_description = Paragraph(item.product.name, body)
        spec_text = ""
        if item.inputs:
            spec_text = Paragraph(_format_inputs(item.product, item.inputs), small)
        rows.append([
            product_description,
            spec_text,
            str(item.quantity),
            _eur(item.unit_price),
            _eur(item.line_total),
        ])

    subtotal = sum(i.line_total for i in items)
    discount_amount = subtotal * discount / 100
    if visible and discount != 0:
        label = "Korting" if discount < 0 else "Meerprijs"
        rows.append(["", "", "", f"{label} ({discount:+.0f} %)", _eur(discount_amount)])

    total = subtotal + discount_amount
    vat = total * 0.21
    total_with_vat = total + vat

    rows.append(["", "", "", "Subtotaal", _eur(subtotal)])
    rows.append(["", "", "", "BTW (21%)", _eur(vat)])
    rows.append(["", "", "", "Totaal incl. BTW", _eur(total_with_vat)])

    products_table = Table(
        rows,
        colWidths=[6.5 * cm, 4 * cm, 2 * cm, 2.25 * cm, 2.25 * cm],
        repeatRows=1,
    )
    products_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#222222")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#f8f8f8")]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#dddddd")),
        ("LINEABOVE", (0, -3), (-1, -3), 1, colors.HexColor("#333333")),
        ("FONTNAME", (2, -2), (-1, -1), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(products_table)

    footer_text = "Disclaimer: Deze offerte is vrijblijvend en geldig voor 14 dagen."

    def _draw_footer(canvas_obj, doc_obj):
        canvas_obj.saveState()
        canvas_obj.setFont("Helvetica", 8)
        page_width, page_height = A4
        canvas_obj.drawCentredString(page_width / 2, 1.5 * cm, footer_text)
        canvas_obj.restoreState()

    doc.build(story, onFirstPage=_draw_footer, onLaterPages=_draw_footer)
    return buffer.getvalue()


def _build_customer_info_table(customer: Customer, body_style) -> Table:
    """Build the customer information section for the header."""
    customer_rows = [
        ["Naam", customer.name or ""],
        ["Adres", customer.address or ""],
        ["E-mail", customer.email or ""],
        ["Telefoon", customer.phone or ""],
    ]
    customer_table = Table(customer_rows, colWidths=[2.5 * cm, 7.5 * cm])
    customer_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    return customer_table


def _build_company_header(company_style) -> Table:
    """Build the company information section with logo for the header."""
    logo_path = Path("template/logo.png")
    
    rows = []
    
    # Add logo if it exists
    if logo_path.exists():
        try:
            img = Image(str(logo_path), width=3 * cm)
            rows.append([img])
        except:
            pass
    
    # Add company info
    rows.extend([
        [Paragraph("Schaverij Hattem", company_style)],
        [Paragraph("De Netelhorst 11", company_style)],
        [Paragraph("8051 KE Hattem", company_style)],
        [Paragraph("Nederland", company_style)],
        [Paragraph("VAT No NL864877389B01", company_style)],
    ])
    
    company_table = Table(rows, colWidths=[5.5 * cm])
    company_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
    ]))
    return company_table