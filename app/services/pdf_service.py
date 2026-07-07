import io
import os
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
    Table,
    TableStyle,
    HRFlowable,
    Image,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

_FONT_REGISTERED = False

NAVY = HexColor("#1e3d59")
NAVY_DARK = HexColor("#14293c")
GRAY_TEXT = HexColor("#555555")
LIGHT_BG = HexColor("#f0f3f7")
BORDER_GRAY = HexColor("#e5e7eb")

_STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "static")
_LOGO_PATH = os.path.join(_STATIC_DIR, "msku-logo.png")


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


def _draw_footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(BORDER_GRAY)
    canvas.setLineWidth(0.5)
    canvas.line(2 * cm, 1.6 * cm, A4[0] - 2 * cm, 1.6 * cm)

    canvas.setFont("DejaVuSans", 8)
    canvas.setFillColor(GRAY_TEXT)
    canvas.drawString(2 * cm, 1.15 * cm, "MSKÜ Bilgi İşlem Daire Başkanlığı")

    canvas.drawRightString(
        A4[0] - 2 * cm, 1.15 * cm, f"Sayfa {canvas.getPageNumber()}"
    )
    canvas.restoreState()


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
        topMargin=1.8 * cm,
        bottomMargin=2.2 * cm,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        title=f"Kategori Raporu - {category_name}",
    )

    org_style = ParagraphStyle(
        "Org",
        fontName="DejaVuSans-Bold",
        fontSize=11,
        textColor=NAVY,
        leading=13,
    )
    title_style = ParagraphStyle(
        "TurkishTitle",
        fontName="DejaVuSans-Bold",
        fontSize=18,
        leading=24,
        textColor=NAVY_DARK,
        spaceBefore=20,
        spaceAfter=16,
    )
    meta_label_style = ParagraphStyle(
        "MetaLabel",
        fontName="DejaVuSans-Bold",
        fontSize=8,
        textColor=GRAY_TEXT,
        leading=11,
    )
    meta_value_style = ParagraphStyle(
        "MetaValue",
        fontName="DejaVuSans",
        fontSize=10,
        textColor=HexColor("#111827"),
        leading=13,
    )
    body_style = ParagraphStyle(
        "TurkishBody",
        fontName="DejaVuSans",
        fontSize=10.5,
        spaceAfter=0,
        alignment=TA_LEFT,
        leading=15,
        textColor=HexColor("#1f2937"),
    )
    empty_style = ParagraphStyle(
        "Empty",
        fontName="DejaVuSans",
        fontSize=11,
        textColor=GRAY_TEXT,
        alignment=TA_LEFT,
        spaceBefore=20,
    )

    story = []

    # --- Kurumsal başlık (logo + kurum adı) ---
    header_cells = []
    if os.path.exists(_LOGO_PATH):
        logo = Image(_LOGO_PATH, width=1.3 * cm, height=1.3 * cm)
        header_cells.append(logo)
    else:
        header_cells.append("")

    header_text = Paragraph(
        "Muğla Sıtkı Koçman Üniversitesi<br/>"
        "<font size=8 color='#6b7280'>Chatbot Veri Yönetim Sistemi</font>",
        org_style,
    )
    header_cells.append(header_text)

    header_table = Table(
        [header_cells], colWidths=[1.6 * cm, None], hAlign="LEFT"
    )
    header_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    story.append(header_table)
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.2, color=NAVY))

    # --- Rapor başlığı ---
    story.append(Paragraph(f"Kategori Raporu: {_escape(category_name)}", title_style))
    story.append(Spacer(1, 6))

    # --- Meta bilgi kutusu ---
    generated_at = datetime.now().strftime("%d.%m.%Y %H:%M")
    meta_table = Table(
        [
            [
                Paragraph("ÇALIŞILAN BİRİM", meta_label_style),
                Paragraph("TOPLAM KAYIT", meta_label_style),
                Paragraph("RAPOR TARİHİ", meta_label_style),
            ],
            [
                Paragraph(_escape(working_unit_name), meta_value_style),
                Paragraph(str(len(entries)), meta_value_style),
                Paragraph(generated_at, meta_value_style),
            ],
        ],
        colWidths=["40%", "25%", "35%"],
    )
    meta_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BG),
                ("BOX", (0, 0), (-1, -1), 0.75, BORDER_GRAY),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (0, 0), 2),
                ("BOTTOMPADDING", (0, 1), (-1, 1), 8),
            ]
        )
    )
    story.append(meta_table)
    story.append(Spacer(1, 22))

    if not entries:
        story.append(Paragraph("Bu kategoride henüz hiç kayıt yok.", empty_style))
    else:
        for i, entry in enumerate(entries, start=1):
            safe_content = _escape(entry.content)

            row = Table(
                [
                    [
                        Paragraph(
                            f'<font color="#ffffff">{i}</font>',
                            ParagraphStyle(
                                "Badge",
                                fontName="DejaVuSans-Bold",
                                fontSize=9,
                                alignment=TA_LEFT,
                            ),
                        ),
                        Paragraph(safe_content, body_style),
                    ]
                ],
                colWidths=[1.1 * cm, None],
            )
            row.setStyle(
                TableStyle(
                    [
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("BACKGROUND", (0, 0), (0, 0), NAVY),
                        ("ALIGN", (0, 0), (0, 0), "CENTER"),
                        ("VALIGN", (0, 0), (0, 0), "MIDDLE"),
                        ("TOPPADDING", (0, 0), (-1, -1), 9),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
                        ("LEFTPADDING", (1, 0), (1, 0), 10),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                        ("BOX", (0, 0), (-1, -1), 0.75, BORDER_GRAY),
                        ("LINEAFTER", (0, 0), (0, 0), 0, BORDER_GRAY),
                    ]
                )
            )
            story.append(row)
            story.append(Spacer(1, 10))

    doc.build(story, onFirstPage=_draw_footer, onLaterPages=_draw_footer)

    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes
