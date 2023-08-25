from marko.inline import InlineElement
from re import Match


class InlineFormula(InlineElement):
    """Represents inline formula element

    Syntax: \\( y = x \\)"""

    pattern = r"[\\\(,$](.*?)[\\\),$]"
    priority = 8

    def __init__(self, match: Match[str]):
        self.formula = match.group(1)
