import unittest
from md2gost.extended_markdown import markdown, Equation


class TestFormula(unittest.TestCase):
    def test_single_line(self):
        res = markdown.parse("$$ test $$").children[0]
        self.assertIsInstance(res, Equation)
        self.assertEqual("test", res.latex_equation)

    def test_multi_line(self):
        res = markdown.parse("""$$
test
$$""").children[0]
        self.assertIsInstance(res, Equation)
        self.assertEqual("test", res.latex_equation)
