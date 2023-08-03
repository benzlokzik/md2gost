from typing import Generator
from dataclasses import dataclass

from docx.shared import Length, Parented, RGBColor
from docx.text.paragraph import Paragraph as DocxParagraph
from docx.enum.text import WD_LINE_SPACING

from . import Renderable
from .paragraph_sizer import ParagraphSizer
from ..layout_tracker import LayoutState
from ..util import create_element
from ..rendered_info import RenderedInfo


@dataclass
class Run:
    text: str
    is_bold: bool = None
    is_italic: bool = None
    color: RGBColor = None


class Paragraph(Renderable):
    def __init__(self, parent: Parented):
        self._docx_paragraph = DocxParagraph(create_element("w:p"), parent)
        self._was_rendered = False

    def add_run(self, text: str, is_bold: bool = None, is_italic: bool = None, color: RGBColor = None):
        docx_run = self._docx_paragraph.add_run(text)
        docx_run.bold = is_bold
        docx_run.italic = is_italic
        docx_run.font.color.rgb = color

    @property
    def style(self):
        return self._docx_paragraph.style

    @style.setter
    def style(self, value: str):
        self._docx_paragraph.style = value

    @property
    def first_line_indent(self):
        return self._docx_paragraph.paragraph_format.first_line_indent

    @first_line_indent.setter
    def first_line_indent(self, value: Length):
        self._docx_paragraph.paragraph_format.first_line_indent = value

    def render(self, previous_rendered: RenderedInfo, layout_state: LayoutState) -> Generator[RenderedInfo, None, None]:
        height_data = ParagraphSizer(
            self._docx_paragraph,
            previous_rendered.docx_element
                      if previous_rendered and isinstance(previous_rendered.docx_element, DocxParagraph) else None,
                      layout_state.max_width).calculate_height()

        # ensure line height, should be removed in the future, when measuring line_height is fixed
        if not self._was_rendered:
            self._docx_paragraph.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
            self._docx_paragraph.paragraph_format.line_spacing = Length(height_data.line_height * height_data.line_spacing)
            self._was_rendered = True

        if layout_state.current_page_height == 0 and layout_state.page > 1:
            height_data.before = 0

        if layout_state.current_page_height + height_data.before + height_data.base <= layout_state.max_height <\
                layout_state.current_page_height + height_data.before + height_data.base + height_data.after:
            # height without space_after fits but with space_after doesn't, so height is remaining page space
            height = layout_state.max_height - layout_state.current_page_height
        elif layout_state.current_page_height + height_data.before + height_data.line_height <= layout_state.max_height <\
                layout_state.current_page_height + height_data.base:
            # first line without line_spacing and space_after first but rest doesn't, so take all remaining space and
            # full height
            height = layout_state.max_height - layout_state.current_page_height + height_data.full
        elif layout_state.current_page_height + height_data.before + height_data.base > layout_state.max_height:
            # still doesn't fit, so take remaining space and full height
            height = layout_state.max_height - layout_state.current_page_height + height_data.full
        else:
            height = height_data.full

        yield RenderedInfo(self._docx_paragraph, False, Length(height))
