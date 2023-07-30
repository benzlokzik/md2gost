import unittest

from md2gost.renderable.paragraph_sizer import Font, _EMUS_PER_PX


class TestFont(unittest.case.TestCase):
    def test_get_text_width(self):
        font = Font("Times New Roman", False, False, 14)
        self.assertEqual(38, font.get_text_width("hello") // _EMUS_PER_PX)

    def test_get_text_width_short(self):
        font = Font("Times New Roman", False, False, 14)
        self.assertEqual(15, font.get_text_width("in") // _EMUS_PER_PX)

    def test_get_text_width_long(self):
        font = Font("Times New Roman", False, False, 14)
        self.assertEqual(245, font.get_text_width("Электроэнцефалографический") // _EMUS_PER_PX)

    def test_get_text_width_bold(self):
        font = Font("Times New Roman", True, False, 14)
        self.assertEqual(39, font.get_text_width("hello") // _EMUS_PER_PX)

    def test_get_text_width_italic(self):
        font = Font("Times New Roman", False, True, 14)
        self.assertEqual(38, font.get_text_width("hello") // _EMUS_PER_PX)

    def test_get_text_width_bold_italic(self):
        font = Font("Times New Roman", False, False, 14)
        self.assertEqual(39, font.get_text_width("hello") // _EMUS_PER_PX)

    def test_get_line_height_times(self):
        font = Font("Times New Roman", False, False, 14)
        self.assertEqual(23, font.get_line_height() // _EMUS_PER_PX)

    def test_get_line_height_times_large(self):
        font = Font("Times New Roman", False, False, 50)
        self.assertEqual(78, font.get_line_height() // _EMUS_PER_PX)

    def test_get_line_height_calibri(self):
        font = Font("Calibri", False, False, 14)
        self.assertEqual(24, font.get_line_height() // _EMUS_PER_PX)

    def test_get_line_height_consolas(self):
        font = Font("Open Sans", False, False, 20)
        self.assertEqual(32, font.get_line_height() // _EMUS_PER_PX)
