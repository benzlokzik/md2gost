import unittest

from md2gost.layout_tracker import LayoutTracker
from md2gost.renderable.paragraph import Paragraph

from . import _create_test_document, _EMUS_PER_PX


class TestParagraph(unittest.TestCase):
    def setUp(self) -> None:
        self._document, self._max_height, self._max_width = _create_test_document()

    def test_render(self):
        paragraph = Paragraph(self._document._body)
        layout_tracker = LayoutTracker(self._max_height, self._max_width)

        paragraph.add_run("hello world")
        info = list(paragraph.render(None, layout_tracker.current_state))[0]

        self.assertEqual(47, info.height / _EMUS_PER_PX)

