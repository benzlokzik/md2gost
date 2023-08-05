import docx
from docx.document import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.shared import Cm, Pt, Mm
from docx.styles.style import _ParagraphStyle

_EMUS_PER_PX = Pt(1) * 72/96


def _create_test_document():
    document: Document = docx.Document()

    document.styles["Normal"].paragraph_format.space_before = 0
    document.styles["Normal"].paragraph_format.space_after = Cm(0.35)
    document.styles["Normal"].paragraph_format.line_spacing = 1.5
    document.styles["Normal"].paragraph_format.first_line_indent = Cm(1.25)
    document.styles["Normal"].font.name = "Times New Roman"
    document.styles["Normal"].font.size = Pt(14)

    document.styles.add_style("Code", WD_STYLE_TYPE.PARAGRAPH)
    document.styles["Code"].paragraph_format.space_before = 0
    document.styles["Code"].paragraph_format.space_after = 0
    document.styles["Code"].paragraph_format.line_spacing = 1
    document.styles["Code"].paragraph_format.first_line_indent = 0
    document.styles["Code"].font.name = "Courier New"
    document.styles["Code"].font.size = Pt(12)

    max_height = Mm(297) - Cm(2) - Cm(2)
    max_width = Mm(210) - Cm(2.5) - Cm(1)

    return document, max_height, max_width
