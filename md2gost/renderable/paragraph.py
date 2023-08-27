from copy import copy
from typing import Generator
from dataclasses import dataclass

from docx.shared import Length, Parented, RGBColor
from docx.text.paragraph import Paragraph as DocxParagraph
from docx.text.paragraph import Run as DocxRun
from docx.enum.text import WD_LINE_SPACING
from docx.opc.constants import RELATIONSHIP_TYPE

from . import Renderable
from .image import Image
from .paragraph_sizer import ParagraphSizer
from ..layout_tracker import LayoutState
from ..util import create_element
from ..rendered_info import RenderedInfo


class Paragraph(Renderable):
    def __init__(self, parent: Parented):
        self._parent = parent
        self._docx_paragraph = DocxParagraph(create_element("w:p"), parent)
        self._images: list[Image] = []

    def add_run(self, text: str, is_bold: bool = None, is_italic: bool = None, color: RGBColor = None):
        # replace all hyphens with non breaking hyphens
        parts = text.split("-")
        for i, part in enumerate(parts):
            docx_run = self._docx_paragraph.add_run(part)
            docx_run.bold = is_bold
            docx_run.italic = is_italic
            docx_run.font.color.rgb = color
            if i != len(parts)-1:
                self._docx_paragraph.add_run()._element.\
                    append(create_element("w:noBreakHyphen"))

    def add_image(self, path: str):
        self._images.append(Image(self._parent, path))

    def add_link(self, text: str, url: str, is_bold: bool = None, is_italic: bool = None):
        r_id = self._parent.part.relate_to(url, RELATIONSHIP_TYPE.HYPERLINK, is_external=True)

        hyperlink = create_element("w:hyperlink", {
            "r:id": r_id
        })

        run = DocxRun(create_element("w:r"), self._docx_paragraph)
        run.text = text
        run.style = "Hyperlink"

        hyperlink.append(run._element)

        self._docx_paragraph._p.append(hyperlink)

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

    def render(self, previous_rendered: RenderedInfo, layout_state: LayoutState)\
            -> Generator[RenderedInfo | Renderable, None, None]:
        if self._docx_paragraph.text or not self._images:
            height_data = ParagraphSizer(
                self._docx_paragraph,
                previous_rendered.docx_element
                          if previous_rendered and isinstance(previous_rendered.docx_element, DocxParagraph) else None,
                          layout_state.max_width).calculate_height()

            if layout_state.current_page_height == 0 and layout_state.page > 1:
                height_data.before = 0

            fitting_lines = 0
            for lines in range(1, height_data.lines+1):
                if height_data.before + ((lines - 1) * height_data.line_spacing + 1) * height_data.line_height \
                        > layout_state.remaining_page_height:
                    break
                fitting_lines += 1

            if fitting_lines == height_data.lines:
                # the whole paragraph fits page
                height = min(height_data.full, layout_state.remaining_page_height)
            elif fitting_lines <= 1 or (height_data.lines-fitting_lines == 1 and height_data.lines == 3):
                # if only no or only one line fits the page, paragraph goes to the next page
                height = layout_state.remaining_page_height + height_data.full
            elif height_data.lines-fitting_lines == 1:
                # if all lines except last fit the page, the last two lines go to the new page
                height = layout_state.remaining_page_height + \
                         height_data.before + height_data.line_height * height_data.line_spacing * 2 \
                         + height_data.after
            else:
                height = layout_state.remaining_page_height + \
                         height_data.before + height_data.line_height * height_data.line_spacing * \
                         (height_data.lines-fitting_lines) + height_data.after

            yield (previous_rendered := RenderedInfo(self._docx_paragraph, False, Length(height)))
            layout_state.add_height(height)

        images = iter(self._images)

        for image in images:
            rendered_image = list(image.render(previous_rendered, copy(layout_state)))
            rendered_image_height = sum([x.height for x in rendered_image])
            if rendered_image:
                previous_rendered = rendered_image[-1]
            if rendered_image_height <= layout_state.remaining_page_height:
                yield from rendered_image
                layout_state.add_height(rendered_image_height)
            else:
                yield image
                break

        yield from images
