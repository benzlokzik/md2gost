from collections.abc import Generator

from docx import Document
from marko.block import BlankLine

from .extended_markdown import markdown
from .renderable.renderable import Renderable
from .renderable_factory import RenderableFactory


class Parser:
    """Parses given markdown string and returns Renderable elements"""

    def __init__(self, document: Document, text: str):
        self.document = document
        self.parsed = markdown.parse(text)

    def parse(self) -> Generator[Renderable, None, None]:
        for marko_element in self.parsed.children:
            if isinstance(marko_element, BlankLine):
                continue

            yield RenderableFactory.create(marko_element, self.document._body)
