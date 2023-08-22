from copy import copy
import os
from typing import Generator, Callable

from docx.shared import Length, Pt, RGBColor
from docx.table import Table

from pygments import highlight
from pygments.formatter import Formatter
from pygments.lexers import get_lexer_by_name
from pygments.styles import get_style_by_name


from .paragraph import Paragraph
from .break_ import Break
from .renderable import Renderable
from ..layout_tracker import LayoutState
from ..rendered_info import RenderedInfo
from ..util import create_element


class DocxParagraphPygmentsFormatter(Formatter):
    def __init__(self, paragraphs: list[Paragraph], creator: Callable[[],Paragraph], **options):
        Formatter.__init__(self, style="sas", **options)
        self._creator = creator
        self._paragraphs = paragraphs
        self._styles = {}

        for token, style in self.style:
            self._styles[token] = style

    def format(self, tokensource, outfile):
        self._paragraphs.append(self._creator())
        for ttype, value in tokensource:
            if value == "\n":
                self._paragraphs.append(self._creator())
            style = self._styles[ttype]
            self._paragraphs[-1].add_run(value.removesuffix("\n"), style["bold"] or None, style["italic"] in style or None,
                                    RGBColor.from_string(style['color']) if style['color'] else None)
        self._paragraphs.pop(-1)  # remove last empty line


LISTING_OFFSET = Pt(31)


class Listing(Renderable):
    def __init__(self, parent, language: str):
        self._language = language
        self.parent = parent
        self.paragraphs: list[Paragraph] = []

    def _create_table(self, parent, width: Length):
        table = Table(create_element("w:tbl", [
            create_element("w:tblPr"),
            create_element("w:tblGrid"),
        ]), parent)
        table.style = "Table Grid"
        table.add_row()
        table.add_column(width)
        table.rows[0].cells[0]._element.remove(table.rows[0].cells[0].paragraphs[0]._element)
        return table

    def set_text(self, text: str):
        def create_paragraph() -> Paragraph:
            paragraph = Paragraph(self.parent, True)
            paragraph.style = "Code"
            return paragraph

        text = text.removesuffix("\n")

        if self._language and "SYNTAX_HIGHLIGHTING" in os.environ and os.environ["SYNTAX_HIGHLIGHTING"] == "1":
            formatter = DocxParagraphPygmentsFormatter(self.paragraphs, lambda: create_paragraph())
            highlight(text, get_lexer_by_name(self._language), formatter)
        else:
            for line in text.removesuffix("\n").split("\n"):
                paragraph = create_paragraph()
                paragraph.add_run(line)
                self.paragraphs.append(paragraph)

    def render(self, previous_rendered: RenderedInfo, layout_state: LayoutState) -> Generator[RenderedInfo, None, None]:
        # layout_state.max_width -= Pt(5)

        table = self._create_table(self.parent, layout_state.max_width)
        previous = None

        table_height = Pt(1)  # table borders, 4 eights of point for each border

        # if first line doesn't fit move listing to the next page
        paragraph_layout_state = copy(layout_state)
        paragraph_layout_state.max_width -= LISTING_OFFSET
        paragraph_rendered_info = next(self.paragraphs[0].render(previous, paragraph_layout_state))
        if paragraph_rendered_info.height + table_height > layout_state.remaining_page_height:
            table_height += layout_state.remaining_page_height
            layout_state.add_height(layout_state.remaining_page_height)

        for paragraph in self.paragraphs:
            paragraph_layout_state = copy(layout_state)
            paragraph_layout_state.max_width -= LISTING_OFFSET
            paragraph_rendered_info = next(paragraph.render(previous, paragraph_layout_state))

            if paragraph_rendered_info.height > layout_state.remaining_page_height:  # todo add before after
                table_rendered_info = RenderedInfo(table, False, table_height)
                yield table_rendered_info

                table_height = Pt(1)  # table borders, 4 eights of point for each border

                continuation_paragraph = Paragraph(self.parent)
                continuation_paragraph.add_run("Продолжение листинга")
                continuation_paragraph.style = "Caption"
                continuation_paragraph.first_line_indent = 0

                break_ = Break(self.parent)
                break_rendered_info = next(
                    break_.render(table_rendered_info, copy(layout_state)))

                if break_rendered_info.height <= layout_state.remaining_page_height:
                    layout_state.add_height(break_rendered_info.height)
                    yield break_rendered_info

                continuation_rendered_info = next(
                    continuation_paragraph.render(None, copy(layout_state)))

                layout_state.add_height(continuation_rendered_info.height)
                yield continuation_rendered_info

                table = self._create_table(self.parent, layout_state.max_width)

                previous = None

                paragraph_layout_state = copy(layout_state)
                paragraph_layout_state.max_width -= LISTING_OFFSET
                paragraph_rendered_info = next(paragraph.render(previous, paragraph_layout_state))

            table._cells[0]._element.append(paragraph_rendered_info.docx_element._element)
            layout_state.add_height(paragraph_rendered_info.height)
            table_height += paragraph_rendered_info.height

            previous = paragraph_rendered_info

        yield RenderedInfo(table, False, table_height)
