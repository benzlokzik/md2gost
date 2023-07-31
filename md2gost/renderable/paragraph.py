from typing import Generator
from dataclasses import dataclass

from docx.shared import Length, Parented, RGBColor
from docx.text.paragraph import Paragraph as DocxParagraph

from . import Renderable
from .paragraph_sizer import ParagraphSizer
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

    def add_run(self, text: str, is_bold: bool = None, is_italic: bool = None, color: RGBColor = None):
        docx_run = self._docx_paragraph.add_run(text)
        docx_run.bold = is_bold
        docx_run.italic = is_italic
        docx_run.font.color.rgb = color

    def render(self, previous_rendered: RenderedInfo, current_page_height: Length, max_height: Length,
               max_width: Length) -> Generator[RenderedInfo, None, None]:
        height_data = ParagraphSizer(
            self._docx_paragraph,
            previous_rendered.docx_element
                      if previous_rendered and isinstance(previous_rendered.docx_element, DocxParagraph) else None,
                      max_width).calculate_height()

        if current_page_height == 0:  # todo: not on the first page
            height_data.before = 0

        if current_page_height + height_data.before + height_data.base <= max_height <\
                current_page_height + height_data.before + height_data.base + height_data.after:
            # height without space_after fits but with space_after doesn't, so height is remaining page space
            height = max_height - current_page_height
        elif current_page_height + height_data.before + height_data.line_height <= max_height <\
                current_page_height + height_data.base:
            # first line without line_spacing and space_after first but rest doesn't, so take all remaining space and
            # full height
            height = max_height - current_page_height + height_data.full
        elif current_page_height + height_data.before + height_data.base > max_height:
            # still doesn't fit, so take remaining space and full height
            height = max_height - current_page_height + height_data.full
        else:
            height = height_data.full

        yield RenderedInfo(self._docx_paragraph, False, Length(height))
