from docx.document import Document
from docx.shared import Length, Cm, Parented, Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

from .renderable import Renderable
from .rendered_info import RenderedInfo
from .util import create_element
from .layout_tracker import LayoutTracker


class Renderer:
    """Renders Renderable elements to docx file"""

    def __init__(self, document: Document):
        self._document: Document = document
        max_height = document.sections[0].page_height - document.sections[0].top_margin - Pt(36+15.6)  # todo add bottom margin detection with footer
        max_width = self._document.sections[0].page_width - self._document.sections[0].top_margin\
            - self._document.sections[0].bottom_margin
        self._layout_tracker = LayoutTracker(max_height, max_width)

    def process(self, renderables: list[Renderable]):
        # add page numbering to the footer
        paragraph = self._document.sections[0].footer.paragraphs[0]
        paragraph.paragraph_format.first_line_indent = 0
        paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        paragraph._p.append(create_element("w:fldSimple", {
            "w:instr": "PAGE \\* MERGEFORMAT"
        }))

        previous_rendered: RenderedInfo | None = None
        for i in range(len(renderables)):
            infos = renderables[i].render(previous_rendered, self._layout_tracker.current_state)

            for info in infos:
                self._add(info.docx_element, info.height)
                previous_rendered = info

    def _add(self, element: Parented, height: Length):
        self._document._body._element.append(
            element._element
        )
        self._layout_tracker.add_height(height)
