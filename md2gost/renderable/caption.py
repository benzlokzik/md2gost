from copy import copy
from typing import Generator

from docx.shared import Parented
from docx.text.paragraph import Paragraph as DocxParagraph
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

from md2gost.layout_tracker import LayoutState
from md2gost.renderable import Renderable
from md2gost.rendered_info import RenderedInfo
from .paragraph_sizer import ParagraphSizer
from ..util import create_element
from .break_ import Break


class Caption(Renderable):
    def __init__(self, parent: Parented, type_: str, text: str):
        self._parent = parent
        self._docx_paragraph = DocxParagraph(create_element("w:p"), parent)

        self._docx_paragraph.style = "Caption"
        self._docx_paragraph.add_run(f"{type_} ? - {text}")

    def center(self):
        self._docx_paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    def render(self, previous_rendered: RenderedInfo, layout_state: LayoutState) -> Generator[
            "RenderedInfo | Renderable", None, None]:
        height_data = ParagraphSizer(
            self._docx_paragraph,
            previous_rendered.docx_element
            if previous_rendered and isinstance(previous_rendered.docx_element, DocxParagraph) else None,
            layout_state.max_width
        ).calculate_height()

        # if two more lines don't fit, move it to the next page (so there is no only caption on the end of the page)
        if ((height_data.lines + 2 - 1) * height_data.line_spacing + 1) * height_data.line_height\
                > layout_state.remaining_page_height:
            break_ = list(Break(self._parent).render(None, copy(layout_state)))
            yield from break_
            layout_state.add_height(sum(x.height for x in break_))
            height_data = ParagraphSizer(
                self._docx_paragraph,
                None,
                layout_state.max_width
            ).calculate_height()

        yield RenderedInfo(self._docx_paragraph, False, height_data.full)

