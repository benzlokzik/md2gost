from marko.inline import InlineElement
from re import Match


class Reference(InlineElement):
    """Represents Reference element

    Syntax: @Type:label"""

    pattern = r"\@([^ ]+):([^ ]+)"

    def __init__(self, match: Match[str]):
        self.type = match.group(1)
        self.name = match.group(2)
