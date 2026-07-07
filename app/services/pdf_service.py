import io
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

_FONT_REGISTERED = False

DARK_TEXT = HexColor("#111827")
GRAY_TEXT = HexColor("#555555")


def _ensure_turkish_font():
    global _FONT_REGISTERED
    if _FONT_REGISTERED:
        return

    import matplotlib
    font_path = matplotlib.get_data_path() + "/fonts/ttf/DejaVuSans.ttf"
    font_path_bold = matplotlib.get_data_path() + "/fonts/ttf/DejaVuSans-Bold.ttf"

    pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))
    pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", font_path_bold))
    _FONT_REGISTERED = True


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def generate_category_pdf(
    category_name: str,
    working_unit_name: str,
    entries: list,
) -> bytes:
    _ensure_turkish_font()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        title=category_name,
    )

    title_style = ParagraphStyle(
        "TurkishTitle",
        fontName="DejaVuSans-Bold",
        fontSize=16,
        leading=20,
        textColor=DARK_TEXT,
        spaceAfter=14,
    )
    meta_style = ParagraphStyle(
        "Meta",
        fontName="DejaVuSans",
        fontSize=9,
        textColor=GRAY_TEXT,
        spaceAfter=14,
    )
    body_style = ParagraphStyle(
        "TurkishBody",
        fontName="DejaVuSans",
        fontSize=11,
        alignment=TA_LEFT,
        leading=16,
        textColor=DARK_TEXT,
        spaceAfter=10,
    )
    empty_style = ParagraphStyle(
        "Empty",
        fontName="DejaVuSans",
        fontSize=11,
        textColor=GRAY_TEXT,
        alignment=TA_LEFT,
    )

    story = []

    story.append(Paragraph(_escape(category_name), title_style))

    generated_at = datetime.now().strftime("%d.%m.%Y %H:%M")
    story.append(
        Paragraph(
            f"{_escape(working_unit_name)} · {len(entries)} kayıt · {generated_at}",
            meta_style,
        )
    )

    if not entries:
        story.append(Paragraph("Bu kategoride henüz hiç kayıt yok.", empty_style))
    else:
        for i, entry in enumerate(entries, start=1):
            safe_content = _escape(entry.content)
            story.append(Paragraph(f"{i}. {safe_content}", body_style))

    doc.build(story)

    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes
