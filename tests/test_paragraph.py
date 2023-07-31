import unittest

import docx
from docx.shared import Mm, Cm, Length
from docx.document import Document

from md2gost.renderable.paragraph_sizer import _EMUS_PER_PX
from md2gost.layout_tracker import LayoutTracker
from md2gost.renderable.paragraph import Paragraph


class TestParagraph(unittest.TestCase):
    def setUp(self) -> None:
        self._document: Document = docx.Document()
        self._document.styles["Normal"].paragraph_format.space_before = 0
        self._document.styles["Normal"].paragraph_format.space_after = Cm(0.35)
        self._document.styles["Normal"].paragraph_format.line_spacing = 1.5
        self._document.styles["Normal"].paragraph_format.first_line_indent = Cm(1.25)

        self._max_height = Mm(297) - Cm(2) - Cm(2)
        self._max_width = Mm(210) - Cm(2.5) - Cm(1)

    def test_render(self):
        paragraph = Paragraph(self._document._body)
        layout_tracker = LayoutTracker(self._max_height, self._max_width)

        paragraph.add_run("hello world")
        info = list(paragraph.render(None, layout_tracker.current_state))[0]

        self.assertEqual(47, info.height / _EMUS_PER_PX)

