from typing import Generator

from docx.shared import Parented, Pt
from docx.text.paragraph import Paragraph as DocxParagraph

from .paragraph_sizer import ParagraphSizer
from ..layout_tracker import LayoutState
from ..rendered_info import RenderedInfo
from ..sub_renderable import SubRenderable
from ..util import create_element
from .renderable import Renderable


class PageBreak(Renderable):
    def __init__(self, parent: Parented):
        self._docx_paragraph = DocxParagraph(create_element("w:p", [
            create_element("w:r", [
                create_element("w:br", {"w:type": "page"})
            ])
        ]), parent)
        self._docx_paragraph.runs[0].font.size = Pt(1)
        self._docx_paragraph.paragraph_format.space_before = 0
        self._docx_paragraph.paragraph_format.space_after = 0

    def render(self, previous_rendered: RenderedInfo, layout_state: LayoutState)\
            -> Generator[RenderedInfo | SubRenderable, None, None]:
        yield RenderedInfo(
            self._docx_paragraph,
            max(layout_state.remaining_page_height, ParagraphSizer(self._docx_paragraph, None, layout_state.max_width).calculate_height().line_height)
        )
