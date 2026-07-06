import io

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

_FONT_REGISTERED = False


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
    )

    title_style = ParagraphStyle(
        "TurkishTitle",
        fontName="DejaVuSans-Bold",
        fontSize=16,
        spaceAfter=6,
    )

    meta_style = ParagraphStyle(
        "TurkishMeta",
        fontName="DejaVuSans",
        fontSize=10,
        spaceAfter=20,
        textColor="#555555",
    )

    body_style = ParagraphStyle(
        "TurkishBody",
        fontName="DejaVuSans",
        fontSize=11,
        spaceAfter=14,
        alignment=TA_LEFT,
        leading=15,
    )

    entry_number_style = ParagraphStyle(
        "TurkishEntryNumber",
        fontName="DejaVuSans-Bold",
        fontSize=10,
        spaceAfter=2,
        textColor="#1F4E79",
    )

    story = []

    story.append(
        Paragraph(f"Kategori Raporu: {category_name}", title_style)
    )

    story.append(
        Paragraph(
            f"Çalışılan Birim: {working_unit_name} — Toplam Kayıt: {len(entries)}",
            meta_style,
        )
    )

    if not entries:
        story.append(Paragraph("Bu kategoride henüz hiç kayıt yok.", body_style))
    else:
        for i, entry in enumerate(entries, start=1):
            story.append(Paragraph(f"Kayıt {i}", entry_number_style))

            safe_content = (
                entry.content
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )

            story.append(Paragraph(safe_content, body_style))
            story.append(Spacer(1, 6))

    doc.build(story)

    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes