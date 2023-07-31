import unittest

from docx.shared import Mm

from md2gost.layout_tracker import LayoutState, LayoutTracker


class TestLayoutState(unittest.TestCase):
    def setUp(self):
        self._state = LayoutState(Mm(297), Mm(210))
        self._state._current_height += Mm(400)

    def test_max_height(self):
        self.assertEqual(Mm(297), self._state.max_height)

    def test_max_width(self):
        self.assertEqual(Mm(210), self._state.max_width)

    def test_current_page_height(self):
        self.assertEqual(Mm(103), self._state.current_page_height)

    def test_remaining_page_height(self):
        self.assertEqual(Mm(194), self._state.remaining_page_height)

    def test_page(self):
        self.assertEqual(2, self._state.page)


class TestLayoutTracker(unittest.TestCase):
    def test_add_height(self):
        layout_tracker = LayoutTracker(Mm(297), Mm(210))
        layout_tracker.add_height(Mm(500))
        self.assertEqual(Mm(203), layout_tracker._state.current_page_height)

    def test_can_fit_to_page(self):
        layout_tracker = LayoutTracker(Mm(297), Mm(210))
        layout_tracker.add_height(Mm(397))

        self.assertTrue(layout_tracker.can_fit_to_page(Mm(100)))
        self.assertTrue(layout_tracker.can_fit_to_page(Mm(197)))
        self.assertFalse(layout_tracker.can_fit_to_page(Mm(198)))
        self.assertFalse(layout_tracker.can_fit_to_page(Mm(500)))

    def test_new_page(self):
        layout_tracker = LayoutTracker(Mm(297), Mm(210))
        layout_tracker.add_height(Mm(497))
        layout_tracker.new_page()

        self.assertEqual(3, layout_tracker.current_state.page)
        self.assertEqual(0, layout_tracker.current_state.current_page_height)
