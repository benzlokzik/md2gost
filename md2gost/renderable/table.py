from copy import copy
from typing import Generator

from docx.oxml import CT_Tbl
from docx.shared import Parented, Length, Pt, Twips
from docx.table import _Row as DocxRow, _Cell as DocxCell, Table as DocxTable

from . import Paragraph
from .break_ import Break
from .renderable import Renderable
from ..layout_tracker import LayoutState
from ..rendered_info import RenderedInfo
from ..util import create_element


CELL_OFFSET = Pt(9) - Twips(108*2)


class Table(Renderable):
    def __init__(self, parent: Parented, rows: int, cols: int):
        self._parent = parent
        self._cols = cols
        sect = parent.part.document.sections[0]

        # todo: style inheritance
        left_margin = Twips(int(parent.part.styles["Normal Table"]._element.xpath("w:tblPr/w:tblCellMar/w:left")[0].attrib["{http://schemas.openxmlformats.org/wordprocessingml/2006/main}w"]))
        right_margin = Twips(int(parent.part.styles["Normal Table"]._element.xpath("w:tblPr/w:tblCellMar/w:right")[0].attrib["{http://schemas.openxmlformats.org/wordprocessingml/2006/main}w"]))

        self._table_width = sect.page_width - sect.left_margin - sect.right_margin + left_margin + right_margin

        self._rows: list[list[list[Paragraph]]] = [[[] for i in range(cols)] for j in range(rows)]

    def add_paragraph_to_cell(self, row: int, col: int) -> Paragraph:
        paragraph = Paragraph(self._parent)
        paragraph.first_line_indent = 0
        paragraph._docx_paragraph.paragraph_format.space_before = 0
        paragraph._docx_paragraph.paragraph_format.space_after = 0
        paragraph._docx_paragraph.paragraph_format.line_spacing = 1
        self._rows[row][col].append(paragraph)
        return paragraph

    def _create_table(self) -> DocxTable:
        table = DocxTable(CT_Tbl.new_tbl(0, self._cols, self._table_width), self._parent)
        table.style = "Table Grid"
        return table

    def render(self, previous_rendered: RenderedInfo, layout_state: LayoutState)\
            -> Generator[RenderedInfo | Renderable, None, None]:
        docx_table = self._create_table()

        table_height = Pt(0.5)  # top border

        for row in self._rows:
            docx_row = DocxRow(create_element("w:tr"), docx_table)
            row_height = 0
            for i in range(self._cols):
                docx_cell = DocxCell(create_element("w:tc"), docx_row)
                docx_cell.width = self._table_width / self._cols
                cell_height = 0
                for paragraph in row[i]:
                    cell_layout_state = LayoutState(
                        layout_state.max_height, layout_state.max_width
                    )
                    cell_layout_state.max_width = self._table_width / self._cols - CELL_OFFSET
                    for paragraph_rendered_info in paragraph.render(None, cell_layout_state):
                        docx_cell._element.append(paragraph_rendered_info.docx_element._element)
                        cell_height += paragraph_rendered_info.height
                    row_height = max(cell_height, row_height)
                docx_row._element.append(docx_cell._element)

            row_height += Pt(0.5)  # bottom row border

            if row_height > layout_state.remaining_page_height:
                table_rendered_info = RenderedInfo(docx_table, table_height)
                yield table_rendered_info

                table_height = Pt(0.5)  # top border

                continuation_paragraph = Paragraph(self._parent)
                continuation_paragraph.add_run("Продолжение таблицы")
                continuation_paragraph.style = "Caption"
                continuation_paragraph.first_line_indent = 0

                break_ = Break(self._parent)
                break_rendered_info = next(
                    break_.render(table_rendered_info, copy(layout_state)))

                if break_rendered_info.height <= layout_state.remaining_page_height:
                    layout_state.add_height(break_rendered_info.height)
                    yield break_rendered_info

                continuation_rendered_info = next(
                    continuation_paragraph.render(None, copy(layout_state)))

                layout_state.add_height(continuation_rendered_info.height)
                yield continuation_rendered_info

                docx_table = self._create_table()

                # previous = None

            docx_table._element.append(docx_row._element)
            layout_state.add_height(row_height)
            table_height += row_height

            # previous = paragraph_rendered_info

        yield RenderedInfo(docx_table, table_height)
