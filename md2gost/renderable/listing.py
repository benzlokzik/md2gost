from copy import copy
from typing import Generator

from docx.shared import Length, Pt
from docx.table import Table

from .paragraph import Paragraph
from .break_ import Break
from .renderable import Renderable
from ..layout_tracker import LayoutState
from ..rendered_info import RenderedInfo
from ..util import create_element


class Listing(Renderable):
    def __init__(self, parent):
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
        for line in text.removesuffix("\n").split("\n"):
            paragraph = Paragraph(self.parent)
            paragraph.add_run(line)
            paragraph.style = "Code"
            self.paragraphs.append(paragraph)

    def render(self, previous_rendered: RenderedInfo, layout_state: LayoutState) -> Generator[RenderedInfo, None, None]:
        # layout_state.max_width -= Pt(5)

        table = self._create_table(self.parent, layout_state.max_width)
        previous = None

        table_height = 0

        for paragraph in self.paragraphs:
            paragraph_rendered_info = next(paragraph.render(previous, layout_state))

            if paragraph_rendered_info.height > layout_state.remaining_page_height:  # todo add before after
                table_rendered_info = RenderedInfo(table, False, table_height)
                yield table_rendered_info

                table_height = 0

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

                paragraph_rendered_info = next(paragraph.render(previous, layout_state))

            table._cells[0]._element.append(paragraph_rendered_info.docx_element._element)
            layout_state.add_height(paragraph_rendered_info.height)
            table_height += paragraph_rendered_info.height

            previous = paragraph_rendered_info

        yield RenderedInfo(table, False, table_height)
