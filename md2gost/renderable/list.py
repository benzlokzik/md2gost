from copy import copy
from typing import Generator

from docx.shared import Pt, Cm, Twips

from . import Paragraph
from .renderable import Renderable
from ..layout_tracker import LayoutState
from ..rendered_info import RenderedInfo


LEVEL_INDENT = Twips(425)


class List(Renderable):
    def __init__(self, parent):
        self._parent = parent
        self._paragraphs: list[Paragraph] = []
        self._last_paragraph_space_after = 0

    def add_item(self, text: str, level: int, numbered: bool):
        paragraph = Paragraph(self._parent)
        paragraph.add_run(text)
        paragraph.style = f"List Number{' '+str(level) if level>1 else ''}" if numbered else "List Bullet"

        # first level indent is a first_line_indent of normal text
        first_indent = self._parent.part.styles["Normal"].paragraph_format.first_line_indent
        # first_indent = 0

        # idk how it works but it works
        paragraph._docx_paragraph.paragraph_format.tab_stops.add_tab_stop(Twips(360))
        paragraph._docx_paragraph.paragraph_format.left_indent = (Twips(425) + first_indent + LEVEL_INDENT*(level-1))
        paragraph._docx_paragraph.paragraph_format.first_line_indent = -Twips(425)

        self._last_paragraph_space_after = paragraph._docx_paragraph.paragraph_format.space_after
        paragraph._docx_paragraph.paragraph_format.space_after = 0

        self._paragraphs.append(paragraph)

    def render(self, previous_rendered: RenderedInfo, layout_state: LayoutState) -> Generator[
            RenderedInfo | Renderable, None, None]:
        self._paragraphs[-1]._docx_paragraph.paragraph_format.space_after = self._last_paragraph_space_after

        for paragraph in self._paragraphs:
            for x in paragraph.render(previous_rendered, copy(layout_state)):
                layout_state.add_height(x.height)
                previous_rendered = x
                yield x
