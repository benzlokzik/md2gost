from collections.abc import Generator

from docx import Document
from marko.block import BlankLine

from .extended_markdown import markdown, Caption
from .renderable.renderable import Renderable
from .renderable_factory import RenderableFactory


class Parser:
    """Parses given markdown string and returns Renderable elements"""

    def __init__(self, document: Document, text: str):
        self._document = document
        self._parsed = markdown.parse(text)
        self._caption: Caption | None = None

    def parse(self) -> Generator[Renderable, None, None]:
        factory = RenderableFactory(self._document._body)

        for marko_element in self._parsed.children:
            if isinstance(marko_element, BlankLine):
                continue

            if isinstance(marko_element, Caption):
                self._caption = marko_element
                continue

            yield factory.create(marko_element, self._caption)
            self._caption = None
