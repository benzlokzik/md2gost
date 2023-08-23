from copy import copy
from typing import Generator

from docx.text.paragraph import Paragraph as DocxParagraph
from docx.shared import Parented, Length

from .break_ import Break
from .paragraph_sizer import ParagraphSizer
from ..layout_tracker import LayoutState
from .paragraph import Paragraph
from ..rendered_info import RenderedInfo


class Heading(Paragraph):
    def __init__(self, parent: Parented, level: int):
        super().__init__(parent)

        self._parent = parent
        self._level = level

        if not 1 <= level <= 9:
            raise ValueError("Heading level must be in range from 1 to 9")

        self.style = f"Heading {level}"

    def render(self, previous_rendered: RenderedInfo, layout_state: LayoutState) -> Generator[RenderedInfo, None, None]:
        if self._level == 1 and layout_state.page != 1:
            yield from Break(self._parent).render(previous_rendered, copy(layout_state))

        height_data = ParagraphSizer(
            self._docx_paragraph,
            previous_rendered.docx_element
            if previous_rendered and isinstance(previous_rendered.docx_element, DocxParagraph) else None,
            layout_state.max_width).calculate_height()

        # if a heading + 2 lines don't fit to the page, they go to the next page
        if ((height_data.lines + 2 - 1) * height_data.line_spacing + 1) * height_data.line_height\
                > layout_state.remaining_page_height:
            # force this behaviour as there could be a table or an image instead of text
            yield from Break(self._parent).render(previous_rendered, copy(layout_state))
            self._docx_paragraph.paragraph_format.space_before = 0  # libreoffice fix
            height = height_data.full - height_data.before
        else:
            height = height_data.full

        yield RenderedInfo(self._docx_paragraph, False, Length(height))
