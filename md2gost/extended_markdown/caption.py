from marko.block import BlockElement
from marko.source import Source
from re import Match


class Caption(BlockElement):
    """Represents caption element

    Syntax: %Type:label Caption text"""

    pattern = r"\%(Таблица|Листинг|Формула)(:([^ ]*?))?( (.+)|$)"

    def __init__(self, match: Match[str]):
        self.category = match.group(1)
        self.unique_name = match.group(3)
        self.text = match.group(5)

    @classmethod
    def match(cls, source: Source) -> Match[str] | None:
        return source.expect_re(cls.pattern)

    @classmethod
    def parse(cls, source: Source) -> Match[str] | None:
        m = source.match
        source.consume()
        return m
