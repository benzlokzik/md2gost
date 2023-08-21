import unittest
from md2gost.extended_markdown import markdown, Formula


class TestFormula(unittest.TestCase):
    def test_single_line(self):
        res = markdown.parse("$$ test $$").children[0]
        self.assertIsInstance(res, Formula)
        self.assertEqual("test", res.formula)

    def test_multi_line(self):
        res = markdown.parse("""$$
test
$$""").children[0]
        self.assertIsInstance(res, Formula)
        self.assertEqual("test", res.formula)
