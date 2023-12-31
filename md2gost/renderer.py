from typing import TYPE_CHECKING
from itertools import chain

from docx.document import Document
from docx.shared import Length, Cm, Parented, Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

from .numberer import Numberer
from .renderable import Renderable
from .renderable.requires_numbering import RequiresNumbering
from .rendered_info import RenderedInfo
from .sub_renderable import SubRenderable
from .util import create_element
from .layout_tracker import LayoutTracker

if TYPE_CHECKING:
    from .debugger import Debugger

BOTTOM_MARGIN = Cm(1.86)


class Renderer:
    """Renders Renderable elements to docx file"""

    def __init__(self, document: Document, debugger: "Debugger | None" = None):
        self._document: Document = document
        self._numberer = Numberer()
        self._debugger = debugger
        max_height = document.sections[0].page_height - document.sections[0].top_margin - BOTTOM_MARGIN# - ((136 / 2) * (Pt(1)*72/96))  # todo add bottom margin detection with footer
        max_width = self._document.sections[0].page_width - self._document.sections[0].left_margin\
            - self._document.sections[0].right_margin
        self._layout_tracker = LayoutTracker(max_height, max_width)

        # add page numbering to the footer
        paragraph = self._document.sections[0].footer.paragraphs[0]
        paragraph.paragraph_format.first_line_indent = 0
        paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        paragraph._p.append(create_element("w:fldSimple", {
            "w:instr": "PAGE \\* MERGEFORMAT"
        }))

        self.previous_rendered = None

        self._to_new_page: list[Renderable] = []

    def process(self, renderables: list[Renderable]):
        for i in range(len(renderables)):
            self.render(renderables[i])

        self._flush_to_new_screen()
        if self._debugger:
            self._debugger.after_rendered()

    def render(self, renderable: Renderable):
        if requires_numbering := isinstance(renderable, RequiresNumbering):
            number = self._numberer.get_current_number(renderable.numbering_category) + 1
            renderable.set_number(number)
        infos = renderable.render(self.previous_rendered, self._layout_tracker.current_state)

        try:
            first = next(infos)
            if isinstance(first, RenderedInfo) and first.height\
                    >= self._layout_tracker.current_state.remaining_page_height:
                self._flush_to_new_screen()
                infos = renderable.render(self.previous_rendered, self._layout_tracker.current_state)
            else:
                infos = chain([first], infos)
        except StopIteration:
            pass

        for info in infos:
            if isinstance(info, SubRenderable):
                if info.add_to_new_page:
                    self._to_new_page.append(info.renderable)
                else:
                    self.render(info.renderable)
            else:
                self._add(info.docx_element, info.height)
                self.previous_rendered = info

        if requires_numbering:
            self._numberer.save_number(renderable.numbering_category, number)

    def _flush_to_new_screen(self):
        while self._to_new_page:
            renderable = self._to_new_page.pop(0)
            if isinstance(renderable, RequiresNumbering):
                number = self._numberer.get_current_number(renderable.numbering_category) + 1
                renderable.set_number(number)
                self._numberer.save_number(renderable.numbering_category, number)
            for info_ in renderable.render(self.previous_rendered, self._layout_tracker.current_state):
                self._add(info_.docx_element, info_.height)


    def _add(self, element: Parented, height: Length):
        self._document._body._element.append(
            element._element
        )
        self._layout_tracker.add_height(height)

        if self._debugger:
            self._debugger.add(element, height)
